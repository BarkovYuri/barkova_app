import json
import os
import time
from urllib import parse, request

from dotenv import load_dotenv

load_dotenv()

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN", "")
BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://backend:8000")


def vk_api(method: str, payload: dict):
    url = f"https://api.vk.com/method/{method}"
    data = {
        **payload,
        "access_token": VK_GROUP_TOKEN,
        "v": "5.199",
    }
    encoded = parse.urlencode(data).encode("utf-8")
    req = request.Request(url, data=encoded, method="POST")

    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def backend_post(path: str, payload: dict):
    url = f"{BACKEND_BASE}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(peer_id: int | str, text: str, keyboard: dict | None = None):
    payload = {
        "peer_id": str(peer_id),
        "message": text,
        "random_id": int(time.time() * 1000),
    }
    if keyboard is not None:
        payload["keyboard"] = json.dumps(keyboard, ensure_ascii=False)

    return vk_api("messages.send", payload)


def answer_message_event(event_id: str, user_id: int | str, peer_id: int | str):
    return vk_api(
        "messages.sendMessageEventAnswer",
        {
            "event_id": str(event_id),
            "user_id": str(user_id),
            "peer_id": str(peer_id),
            "event_data": json.dumps(
                {"type": "show_snackbar", "text": "Обрабатываю..."},
                ensure_ascii=False,
            ),
        },
    )


def parse_payload(raw_payload):
    if not raw_payload:
        return None
    try:
        if isinstance(raw_payload, dict):
            return raw_payload
        return json.loads(raw_payload)
    except Exception:
        return None


def parse_connect_token(text: str, payload: dict | None):
    if payload and isinstance(payload, dict):
        if payload.get("cmd") == "connect" and payload.get("token"):
            return str(payload["token"]).strip()

    text = (text or "").strip()
    if text.startswith("connect_"):
        return text.replace("connect_", "", 1).strip()

    return None


def should_send_vk_greeting(user_id: int | str) -> bool:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

    from django.core.cache import cache

    cache_key = f"vk_greeting_sent:{user_id}"
    if cache.get(cache_key):
        return False

    cache.set(cache_key, "1", timeout=365 * 24 * 60 * 60)
    return True


def get_active_appointment_for_vk_user(user_id: int | str):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

    from apps.appointments.models import Appointment

    return (
        Appointment.objects.select_related("slot")
        .filter(vk_user_id=str(user_id), status__in=["new", "confirmed"])
        .order_by("-created_at")
        .first()
    )


def get_dialog_state(user_id: int | str):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

    from apps.notifications.models import VKDialogState

    state, _ = VKDialogState.objects.select_related("appointment", "appointment__slot").get_or_create(
        user_id=str(user_id)
    )
    return state


def set_dialog_state(user_id: int | str, peer_id: int | str, state_name: str, appointment=None):
    state = get_dialog_state(user_id)
    state.peer_id = str(peer_id)
    state.state = state_name
    state.appointment = appointment
    state.save(update_fields=["peer_id", "state", "appointment", "updated_at"])
    return state


def reset_dialog_state(user_id: int | str, peer_id: int | str):
    return set_dialog_state(user_id, peer_id, "idle", appointment=None)


def get_dialog_appointment(user_id: int | str):
    state = get_dialog_state(user_id)
    if state.appointment_id:
        return state.appointment
    return None


def get_effective_appointment(user_id: int | str):
    dialog_appointment = get_dialog_appointment(user_id)
    if dialog_appointment and dialog_appointment.status in {"new", "confirmed"}:
        return dialog_appointment
    return get_active_appointment_for_vk_user(user_id)


def build_manage_keyboard(appointment):
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "label": "Подтвердить",
                        "payload": json.dumps(
                            {
                                "cmd": "confirm",
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "positive",
                },
                {
                    "action": {
                        "type": "callback",
                        "label": "Отменить",
                        "payload": json.dumps(
                            {
                                "cmd": "cancel_request",
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "negative",
                },
            ]
        ],
    }


def build_cancel_confirm_keyboard(appointment):
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "label": "Подтвердить отмену",
                        "payload": json.dumps(
                            {
                                "cmd": "cancel_confirm",
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "negative",
                },
                {
                    "action": {
                        "type": "callback",
                        "label": "Оставить запись",
                        "payload": json.dumps(
                            {
                                "cmd": "cancel_keep",
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "secondary",
                },
            ]
        ],
    }


def handle_connect(user_id: int, peer_id: int, token: str):
    try:
        backend_post(
            "/api/appointments/vk/prelink/link/",
            {
                "token": token,
                "user_id": str(user_id),
                "peer_id": str(peer_id),
            },
        )
        send_message(
            peer_id,
            "✅ VK подключён. Теперь сюда будут приходить уведомления о записи.",
        )
    except Exception as exc:
        print("VK connect error:", exc)


def handle_callback_action(user_id: int, peer_id: int, payload: dict):
    cmd = payload.get("cmd")
    appointment_id = payload.get("appointment_id")
    token = payload.get("token")

    appointment = get_effective_appointment(user_id)

    # Если callback пришел по конкретной записи — предпочитаем ее
    if appointment and appointment_id and str(appointment.id) != str(appointment_id):
        if appointment.status not in {"new", "confirmed"}:
            appointment = None

    if cmd == "cancel_request":
        if appointment:
            send_message(
                peer_id,
                (
                    "Вы действительно хотите отменить запись?\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
                keyboard=build_cancel_confirm_keyboard(appointment),
            )
            set_dialog_state(user_id, peer_id, "confirm_cancel", appointment)
        return

    if cmd == "cancel_keep":
        if appointment:
            send_message(peer_id, "✅ Запись оставлена без изменений.")
            set_dialog_state(user_id, peer_id, "has_active_appointment", appointment)
        else:
            reset_dialog_state(user_id, peer_id)
        return

    if cmd == "cancel_confirm":
        cmd = "cancel"

    if cmd not in {"confirm", "cancel", "yes", "no", "doctor"}:
        return

    try:
        result = backend_post(
            "/api/appointments/vk/action/",
            {
                "appointment_id": appointment_id,
                "token": token,
                "action": cmd,
                "user_id": str(user_id),
            },
        )

        # Если действие не изменило состояние, не переключаемся хаотично
        changed = bool(result.get("changed", True))

        if cmd == "confirm":
            if appointment and changed:
                set_dialog_state(user_id, peer_id, "has_active_appointment", appointment)
            elif appointment:
                set_dialog_state(user_id, peer_id, "has_active_appointment", appointment)
            else:
                reset_dialog_state(user_id, peer_id)
        elif cmd in {"cancel", "no"}:
            reset_dialog_state(user_id, peer_id)
        elif cmd == "doctor":
            if appointment:
                set_dialog_state(user_id, peer_id, "has_active_appointment", appointment)
            else:
                reset_dialog_state(user_id, peer_id)
        else:
            reset_dialog_state(user_id, peer_id)

    except Exception as exc:
        print("VK action error:", exc)


def handle_new_message_event(event: dict):
    message = event.get("object", {}).get("message", {})
    text = (message.get("text") or "").strip()
    peer_id = message.get("peer_id")
    from_id = message.get("from_id")
    payload = parse_payload(message.get("payload"))

    if not peer_id or not from_id:
        return

    token = parse_connect_token(text, payload)
    if token:
        handle_connect(from_id, peer_id, token)
        return

    auto_linked = False
    try:
        result = backend_post(
            "/api/appointments/vk/auto-link/",
            {
                "user_id": str(from_id),
                "peer_id": str(peer_id),
            },
        )
        auto_linked = result.get("status") == "linked"
    except Exception as exc:
        print("VK auto-link error:", exc)

    if auto_linked:
        send_message(
            peer_id,
            "✅ Диалог с сообществом подключён.\nТеперь вы будете получать уведомления здесь.\n\nВернитесь на сайт и завершите запись.",
        )
        return

    dialog_state = get_dialog_state(from_id)
    appointment = get_effective_appointment(from_id)

    # Если активной записи нет — чистим state и максимум один раз шлем приветствие
    if not appointment:
        reset_dialog_state(from_id, peer_id)
        if should_send_vk_greeting(from_id):
            send_message(
                peer_id,
                "Здравствуйте. Как только доктор освободится, вам обязательно ответят.",
            )
        return

    same_appointment = (
        dialog_state.appointment is not None
        and dialog_state.appointment.id == appointment.id
    )

    # Если уже в сценарии этой же записи, не спамим повторными меню на обычный текст
    if dialog_state.state in {"has_active_appointment", "confirm_cancel"} and same_appointment:
        return

    send_message(
        peer_id,
        (
            "У вас есть активная запись.\n"
            f"Дата: {appointment.slot.date}\n"
            f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
            f"{appointment.slot.end_time.strftime('%H:%M')}\n\n"
            "Используйте кнопки ниже, если хотите изменить запись."
        ),
        keyboard=build_manage_keyboard(appointment),
    )
    set_dialog_state(from_id, peer_id, "has_active_appointment", appointment)


def handle_callback_event(event: dict):
    event_object = event.get("object", {})
    event_id = event_object.get("event_id")
    user_id = event_object.get("user_id")
    peer_id = event_object.get("peer_id")
    payload = parse_payload(event_object.get("payload"))

    if not event_id or not user_id or not peer_id:
        return

    try:
        answer_message_event(event_id, user_id, peer_id)
    except Exception as exc:
        print("VK message_event answer error:", exc)

    if not payload:
        return

    handle_callback_action(user_id, peer_id, payload)
import json
import os
import time
from urllib import parse, request

from dotenv import load_dotenv

load_dotenv()

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN", "")
BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")


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


def parse_payload(raw_payload):
    if not raw_payload:
        return None
    try:
        return json.loads(raw_payload)
    except Exception:
        return None


def parse_connect_token(text: str, payload: dict | None):
    # Сценарий через payload
    if payload and isinstance(payload, dict):
        if payload.get("cmd") == "connect" and payload.get("token"):
            return str(payload["token"]).strip()

    # Сценарий через текстовую команду
    text = (text or "").strip()
    if text.startswith("connect_"):
        return text.replace("connect_", "", 1).strip()

    return None


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


def build_cancel_keyboard(appointment):
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Подтвердить отмену",
                        "payload": json.dumps(
                            {
                                "cmd": "cancel",
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
                        "type": "text",
                        "label": "Оставить запись",
                        "payload": json.dumps(
                            {
                                "cmd": "keep",
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
        send_message(peer_id, f"Не удалось подключить VK: {exc}")


def handle_action(user_id: int, peer_id: int, payload: dict):
    cmd = payload.get("cmd")
    appointment_id = payload.get("appointment_id")
    token = payload.get("token")

    if cmd == "keep":
        send_message(peer_id, "✅ Запись оставлена без изменений.")
        return

    if cmd not in {"confirm", "cancel"}:
        return

    try:
        backend_post(
            "/api/appointments/vk/action/",
            {
                "appointment_id": appointment_id,
                "token": token,
                "action": cmd,
                "user_id": str(user_id),
            },
        )

        if cmd == "confirm":
            send_message(peer_id, "✅ Запись подтверждена.")
        else:
            send_message(peer_id, "❌ Запись отменена.")
    except Exception as exc:
        send_message(peer_id, f"Ошибка: {exc}")


def handle_regular_user_message(user_id: int, peer_id: int, text: str):
    """
    Логика для обычных сообщений:
    - если активной записи нет -> нейтральный автоответ
    - если активная запись есть -> предлагаем отмену, а не отвечаем 'нет записи'
    """
    appointment = get_active_appointment_for_vk_user(user_id)

    if not appointment:
        send_message(
            peer_id,
            "Здравствуйте. Как только доктор освободится, вам обязательно ответят.",
        )
        return

    send_message(
        peer_id,
        (
            "Если вам нужно отменить запись, нажмите кнопку ниже.\n"
            f"Дата: {appointment.slot.date}\n"
            f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
            f"{appointment.slot.end_time.strftime('%H:%M')}"
        ),
        keyboard=build_cancel_keyboard(appointment),
    )


def handle_message_event(event: dict):
    message = event.get("object", {}).get("message", {})
    text = (message.get("text") or "").strip()
    peer_id = message.get("peer_id")
    from_id = message.get("from_id")
    payload = parse_payload(message.get("payload"))

    if not peer_id or not from_id:
        return

    # 1. Сначала пытаемся обработать привязку с сайта
    token = parse_connect_token(text, payload)
    if token:
        handle_connect(from_id, peer_id, token)
        return

    # 2. Затем кнопки подтверждения/отмены
    if payload and payload.get("cmd") in {"confirm", "cancel", "keep"}:
        handle_action(from_id, peer_id, payload)
        return

    # 3. Любое обычное сообщение
    handle_regular_user_message(from_id, peer_id, text)
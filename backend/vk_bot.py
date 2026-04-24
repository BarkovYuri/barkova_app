"""
VK (VKontakte) bot implementation for clinic appointment management.

This module implements a VK bot that handles:
- Community (group) messaging integration
- Account linking/unlinking via prelink tokens
- Auto-linking when user sends message to community
- Appointment confirmation/cancellation with inline buttons
- Dialog state management to track user actions
- Rate-limiting for menu messages (anti-spam)

The bot uses long polling to receive updates from VK API.
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional
from urllib import error, parse, request

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN", "")
BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://backend:8000")
VK_API_VERSION = os.getenv("VK_API_VERSION", "5.199")
BOOKING_LINK = os.getenv("BOOKING_LINK", "https://doctor-barkova.ru/booking")
API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "30"))
BOT_POLLING_TIMEOUT = int(os.getenv("BOT_POLLING_TIMEOUT", "25"))


def vk_api(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call VK API.

    Args:
        method: API method name (e.g., 'messages.send')
        payload: Request parameters

    Returns:
        API response as dictionary

    Raises:
        error.HTTPError: If API request fails
        json.JSONDecodeError: If response is not valid JSON
    """
    url = f"https://api.vk.com/method/{method}"
    data = {
        **payload,
        "access_token": VK_GROUP_TOKEN,
        "v": VK_API_VERSION,
    }
    encoded = parse.urlencode(data).encode("utf-8")
    req = request.Request(url, data=encoded, method="POST")

    try:
        with request.urlopen(req, timeout=API_REQUEST_TIMEOUT) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            logger.debug(f"VK API call successful: {method}")
            return response_data
    except error.HTTPError as exc:
        logger.error(f"VK API HTTP Error {exc.code}: {exc.reason}")
        raise
    except Exception as exc:
        logger.error(f"VK API error: {exc}")
        raise


def backend_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    POST request to backend API.

    Args:
        path: API endpoint path
        payload: Request body

    Returns:
        API response as dictionary

    Raises:
        error.HTTPError: If request fails
        json.JSONDecodeError: If response is not valid JSON
    """
    url = f"{BACKEND_BASE}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=API_REQUEST_TIMEOUT) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            logger.debug(f"Backend API call successful: POST {path}")
            return response_data
    except error.HTTPError as exc:
        logger.error(f"Backend API HTTP Error {exc.code}: {exc.reason}")
        raise
    except Exception as exc:
        logger.error(f"Backend API error: {exc}")
        raise


def send_message(
    peer_id: int | str, text: str, keyboard: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send message to VK user.

    Args:
        peer_id: VK peer ID (user or chat)
        text: Message text
        keyboard: Optional inline keyboard

    Returns:
        API response
    """
    payload = {
        "peer_id": str(peer_id),
        "message": text,
        "random_id": int(time.time() * 1000),
    }
    if keyboard is not None:
        payload["keyboard"] = json.dumps(keyboard, ensure_ascii=False)

    return vk_api("messages.send", payload)


def answer_message_event(event_id: str, user_id: int | str, peer_id: int | str) -> Dict[str, Any]:
    """
    Send event answer (show loading indicator in VK).

    Args:
        event_id: Event ID from button press
        user_id: VK user ID
        peer_id: VK peer ID

    Returns:
        API response
    """
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


def parse_payload(raw_payload: Any) -> Optional[Dict[str, Any]]:
    """
    Parse payload from VK message.

    Handles both dict and JSON string formats.

    Args:
        raw_payload: Raw payload from VK API

    Returns:
        Parsed payload dictionary or None if invalid
    """
    if not raw_payload:
        return None

    try:
        if isinstance(raw_payload, dict):
            return raw_payload
        return json.loads(raw_payload)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.debug(f"Failed to parse payload: {exc}")
        return None


def parse_connect_token(text: str, payload: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Extract connection token from message.

    Supports:
    - Payload format: {"cmd": "connect", "token": "..."}
    - Text format: "connect_TOKEN"

    Args:
        text: Message text
        payload: Parsed message payload

    Returns:
        Token string or None if not found
    """
    if payload and isinstance(payload, dict):
        if payload.get("cmd") == "connect" and payload.get("token"):
            return str(payload["token"]).strip()

    text = (text or "").strip()
    if text.startswith("connect_"):
        return text.replace("connect_", "", 1).strip()

    return None


def should_send_vk_greeting(user_id: int | str) -> bool:
    """
    Check if greeting should be sent to VK user (once per day).

    Args:
        user_id: VK user ID

    Returns:
        True if greeting can be sent, False if already sent today
    """
    from apps.integrations.base_bot import BaseBot

    BaseBot.setup_django()

    from django.core.cache import cache

    cache_key = f"vk_greeting_sent:{user_id}"
    if cache.get(cache_key):
        return False

    cache.set(cache_key, "1", timeout=365 * 24 * 60 * 60)
    return True


def get_active_appointment_for_vk_user(user_id: int | str) -> Optional[Any]:
    """
    Get active appointment for VK user.

    Args:
        user_id: VK user ID

    Returns:
        Appointment object or None if not found
    """
    from apps.appointments.models import Appointment

    return (
        Appointment.objects.select_related("slot")
        .filter(vk_user_id=str(user_id), status__in=["new", "confirmed"])
        .order_by("-created_at")
        .first()
    )


def get_dialog_state(user_id: int | str) -> Any:
    """
    Get or create dialog state for VK user.

    Args:
        user_id: VK user ID

    Returns:
        VKDialogState object
    """
    from apps.notifications.models import VKDialogState

    state, _ = VKDialogState.objects.select_related("appointment", "appointment__slot").get_or_create(
        user_id=str(user_id)
    )
    return state


def set_dialog_state(
    user_id: int | str,
    peer_id: int | str,
    state_name: str,
    appointment: Optional[Any] = None,
    last_menu_kind: Optional[str] = None,
    touch_action: bool = False,
) -> Any:
    """
    Update dialog state for VK user.

    Args:
        user_id: VK user ID
        peer_id: VK peer ID
        state_name: New state name
        appointment: Optional appointment to link
        last_menu_kind: Last menu kind shown to user
        touch_action: Whether to update last_action_at timestamp

    Returns:
        Updated VKDialogState object
    """
    from django.utils import timezone

    state = get_dialog_state(user_id)
    state.peer_id = str(peer_id)
    state.state = state_name
    state.appointment = appointment

    update_fields = ["peer_id", "state", "appointment", "updated_at"]

    if last_menu_kind is not None:
        state.last_menu_kind = last_menu_kind
        update_fields.append("last_menu_kind")

    if touch_action:
        state.last_action_at = timezone.now()
        update_fields.append("last_action_at")

    state.save(update_fields=update_fields)
    return state


def reset_dialog_state(user_id: int | str, peer_id: int | str) -> Any:
    """
    Reset dialog state to idle.

    Args:
        user_id: VK user ID
        peer_id: VK peer ID

    Returns:
        Reset VKDialogState object
    """
    return set_dialog_state(
        user_id,
        peer_id,
        "idle",
        appointment=None,
        last_menu_kind="none",
    )


def can_send_menu(dialog_state: Any, menu_kind: str, cooldown_seconds: int = 600) -> bool:
    """
    Check if menu can be sent (rate limiting).

    Args:
        dialog_state: VKDialogState object
        menu_kind: Menu type identifier
        cooldown_seconds: Minimum seconds between same menu type

    Returns:
        True if menu can be sent, False if still in cooldown
    """
    from django.utils import timezone

    if dialog_state.last_menu_kind != menu_kind:
        return True

    if not dialog_state.last_menu_sent_at:
        return True

    delta = timezone.now() - dialog_state.last_menu_sent_at
    return delta.total_seconds() >= cooldown_seconds


def mark_menu_sent(user_id: int | str, menu_kind: str) -> Any:
    """
    Mark menu as sent to user (for rate limiting).

    Args:
        user_id: VK user ID
        menu_kind: Menu type identifier

    Returns:
        Updated VKDialogState object
    """
    from django.utils import timezone

    state = get_dialog_state(user_id)
    state.last_menu_kind = menu_kind
    state.last_menu_sent_at = timezone.now()
    state.save(update_fields=["last_menu_kind", "last_menu_sent_at", "updated_at"])
    return state


def get_dialog_appointment(user_id: int | str) -> Optional[Any]:
    """
    Get appointment from dialog state.

    Args:
        user_id: VK user ID

    Returns:
        Appointment from dialog state or None
    """
    state = get_dialog_state(user_id)
    if state.appointment_id:
        return state.appointment
    return None


def get_effective_appointment(user_id: int | str) -> Optional[Any]:
    """
    Get most recent active appointment for user.

    Checks both dialog state and active appointments in database.

    Args:
        user_id: VK user ID

    Returns:
        Appointment object or None if not found
    """
    dialog_appointment = get_dialog_appointment(user_id)
    if dialog_appointment and dialog_appointment.status in {"new", "confirmed"}:
        return dialog_appointment
    return get_active_appointment_for_vk_user(user_id)


def build_booking_keyboard() -> Dict[str, Any]:
    """
    Build keyboard for booking action.

    Returns:
        VK keyboard dict
    """
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "open_link",
                        "label": "Записаться на консультацию",
                        "link": BOOKING_LINK,
                        "payload": json.dumps({"cmd": "open_booking"}, ensure_ascii=False),
                    }
                }
            ]
        ],
    }


def build_manage_keyboard(appointment: Any) -> Dict[str, Any]:
    """
    Build keyboard for appointment management.

    Args:
        appointment: Appointment object

    Returns:
        VK keyboard dict
    """
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "label": "Отменить запись",
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
                {
                    "action": {
                        "type": "callback",
                        "label": "Связь с врачом",
                        "payload": json.dumps(
                            {
                                "cmd": "doctor",
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "primary",
                },
            ]
        ],
    }


def build_cancel_confirm_keyboard(appointment: Any) -> Dict[str, Any]:
    """
    Build keyboard for cancellation confirmation.

    Args:
        appointment: Appointment object

    Returns:
        VK keyboard dict
    """
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


def build_active_root_keyboard(appointment: Any) -> Dict[str, Any]:
    """
    Build keyboard for active appointment (root menu).

    Args:
        appointment: Appointment object

    Returns:
        VK keyboard dict
    """
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "label": "Управление записью",
                        "payload": json.dumps(
                            {
                                "cmd": "manage",
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "primary",
                }
            ]
        ],
    }


def handle_connect(user_id: int, peer_id: int, token: str) -> None:
    """
    Handle account connection via token.

    Args:
        user_id: VK user ID
        peer_id: VK peer ID
        token: Prelink token from appointment booking
    """
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
        logger.info(f"VK user {user_id} successfully connected")
    except Exception as exc:
        logger.exception(f"VK connect error for user {user_id}: {exc}")


def handle_callback_action(user_id: int, peer_id: int, payload: Dict[str, Any]) -> None:
    """
    Handle callback action from inline button.

    Args:
        user_id: VK user ID
        peer_id: VK peer ID
        payload: Button payload dictionary
    """
    cmd = payload.get("cmd")
    appointment_id = payload.get("appointment_id")
    token = payload.get("token")

    appointment = get_effective_appointment(user_id)

    if appointment and appointment_id and str(appointment.id) != str(appointment_id):
        if appointment.status not in {"new", "confirmed"}:
            appointment = None

    # Handle "manage" action
    if cmd == "manage":
        if appointment:
            slot = appointment.slot
            send_message(
                peer_id,
                (
                    "Что вы хотите сделать с записью?\n"
                    f"📅 {slot.date.strftime('%d.%m.%Y')}\n"
                    f"🕐 {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}"
                ),
                keyboard=build_manage_keyboard(appointment),
            )
            set_dialog_state(
                user_id,
                peer_id,
                "has_active_appointment",
                appointment,
                last_menu_kind="manage",
                touch_action=True,
            )
            mark_menu_sent(user_id, "manage")
        return

    # Handle "cancel_request" action
    if cmd == "cancel_request":
        if appointment:
            slot = appointment.slot
            send_message(
                peer_id,
                (
                    "Вы действительно хотите отменить запись?\n"
                    f"📅 {slot.date.strftime('%d.%m.%Y')}\n"
                    f"🕐 {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}"
                ),
                keyboard=build_cancel_confirm_keyboard(appointment),
            )
            set_dialog_state(
                user_id,
                peer_id,
                "confirm_cancel",
                appointment,
                last_menu_kind="cancel_confirm",
                touch_action=True,
            )
            mark_menu_sent(user_id, "cancel_confirm")
        return

    # Handle "cancel_keep" action
    if cmd == "cancel_keep":
        if appointment:
            send_message(
                peer_id,
                "✅ Запись оставлена без изменений.",
                keyboard=build_active_root_keyboard(appointment),
            )
            set_dialog_state(
                user_id,
                peer_id,
                "has_active_appointment",
                appointment,
                last_menu_kind="active_root",
                touch_action=True,
            )
        else:
            reset_dialog_state(user_id, peer_id)
        return

    # Normalize cancel_confirm to cancel action
    if cmd == "cancel_confirm":
        cmd = "cancel"

    # Send action to backend
    if cmd not in {"confirm", "cancel", "yes", "no", "doctor"}:
        logger.warning(f"Unknown command: {cmd}")
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

        changed = bool(result.get("changed", True))

        # Update dialog state based on action
        if cmd == "confirm":
            if appointment:
                set_dialog_state(
                    user_id,
                    peer_id,
                    "has_active_appointment",
                    appointment,
                    last_menu_kind="active_root",
                    touch_action=True,
                )
            else:
                reset_dialog_state(user_id, peer_id)

        elif cmd in {"cancel", "no"}:
            reset_dialog_state(user_id, peer_id)

        elif cmd == "doctor":
            if appointment:
                set_dialog_state(
                    user_id,
                    peer_id,
                    "has_active_appointment",
                    appointment,
                    last_menu_kind="active_root",
                    touch_action=True,
                )
            else:
                reset_dialog_state(user_id, peer_id)

        else:
            reset_dialog_state(user_id, peer_id)

        logger.info(f"VK action {cmd} processed for user {user_id}")

    except Exception as exc:
        logger.exception(f"VK action error for user {user_id}: {exc}")


def handle_new_message_event(event: Dict[str, Any]) -> None:
    """
    Handle new message from VK user.

    Args:
        event: Message event from VK API
    """
    message = event.get("object", {}).get("message", {})
    text = (message.get("text") or "").strip()
    peer_id = message.get("peer_id")
    from_id = message.get("from_id")
    payload = parse_payload(message.get("payload"))

    if not peer_id or not from_id:
        logger.warning("Message event without peer_id or from_id")
        return

    # Check for connect token
    token = parse_connect_token(text, payload)
    if token:
        handle_connect(from_id, peer_id, token)
        return

    # Try auto-linking
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
        logger.exception(f"VK auto-link error for user {from_id}: {exc}")

    if auto_linked:
        send_message(
            peer_id,
            "✅ Диалог с сообществом подключён.\nТеперь вы будете получать уведомления здесь.\n\nВернитесь на сайт и завершите запись.",
        )
        return

    # Handle existing users
    dialog_state = get_dialog_state(from_id)
    appointment = get_effective_appointment(from_id)

    if not appointment:
        reset_dialog_state(from_id, peer_id)
        dialog_state = get_dialog_state(from_id)

        if can_send_menu(dialog_state, "booking", cooldown_seconds=600):
            send_message(
                peer_id,
                "Здравствуйте. Чтобы записаться на консультацию, нажмите кнопку ниже.",
                keyboard=build_booking_keyboard(),
            )
            mark_menu_sent(from_id, "booking")
        return

    # Show active appointment menu
    same_appointment = (
        dialog_state.appointment is not None and dialog_state.appointment.id == appointment.id
    )

    if same_appointment:
        if can_send_menu(dialog_state, "active_root", cooldown_seconds=600):
            slot = appointment.slot
            send_message(
                peer_id,
                (
                    "У вас есть активная запись.\n"
                    f"📅 {slot.date.strftime('%d.%m.%Y')}\n"
                    f"🕐 {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n\n"
                    "Нажмите «Управление записью», чтобы открыть доступные действия."
                ),
                keyboard=build_active_root_keyboard(appointment),
            )
            set_dialog_state(
                from_id,
                peer_id,
                "has_active_appointment",
                appointment,
                last_menu_kind="active_root",
            )
            mark_menu_sent(from_id, "active_root")
        return


def handle_callback_event(event: Dict[str, Any]) -> None:
    """
    Handle callback event from VK inline button.

    Args:
        event: Callback event from VK API
    """
    event_object = event.get("object", {})
    event_id = event_object.get("event_id")
    user_id = event_object.get("user_id")
    peer_id = event_object.get("peer_id")
    payload = parse_payload(event_object.get("payload"))

    if not event_id or not user_id or not peer_id:
        logger.warning("Callback event missing required fields")
        return

    # Send event answer (show loading indicator)
    try:
        answer_message_event(event_id, user_id, peer_id)
    except Exception as exc:
        logger.exception(f"VK message_event answer error: {exc}")

    if not payload:
        return

    handle_callback_action(user_id, peer_id, payload)


def main() -> None:
    """
    Start bot's main polling loop.

    This function:
    1. Initializes Django ORM
    2. Starts long polling for VK updates
    3. Handles all incoming messages and callbacks
    4. Implements error recovery with exponential backoff
    """
    from apps.integrations.base_bot import BaseBot

    # Initialize Django once
    BaseBot.setup_django()

    retry_count = 0
    max_retries = 5

    logger.info("VK bot started")

    while True:
        try:
            payload = {
                "act": "a_check_updates",
                "wait": BOT_POLLING_TIMEOUT,
                "mode": 2,  # messages + events
                "version": 3,
            }

            data = vk_api("groups.getLongPollServer", {})

            if "error" in data:
                logger.error(f"Failed to get long poll server: {data.get('error')}")
                time.sleep(5)
                continue

            server = data.get("response", {}).get("server")
            if not server:
                logger.error("No polling server returned")
                time.sleep(5)
                continue

            # Poll for updates
            url = f"{server}&{parse.urlencode(payload)}"
            from urllib import request

            req = request.Request(url, method="GET")
            with request.urlopen(req, timeout=BOT_POLLING_TIMEOUT + 5) as response:
                updates = json.loads(response.read().decode("utf-8"))

            for update in updates.get("updates", []):
                try:
                    event_type = update.get("type")

                    if event_type == "message_new":
                        handle_new_message_event(update)
                    elif event_type == "message_event":
                        handle_callback_event(update)

                except Exception as exc:
                    logger.exception(f"Error processing update: {exc}")

            # Reset retry counter on success
            retry_count = 0

        except error.HTTPError as exc:
            retry_count += 1
            logger.error(f"VK polling HTTP Error {exc.code} (retry {retry_count}/{max_retries})")
            wait_time = min(2**retry_count, 60)  # Exponential backoff
            time.sleep(wait_time)

        except Exception as exc:
            retry_count += 1
            logger.exception(f"VK polling error (retry {retry_count}/{max_retries})")
            wait_time = min(2**retry_count, 60)  # Exponential backoff
            time.sleep(wait_time)

            if retry_count >= max_retries:
                logger.critical(f"Max retries ({max_retries}) exceeded, restarting bot")
                retry_count = 0


if __name__ == "__main__":
    main()

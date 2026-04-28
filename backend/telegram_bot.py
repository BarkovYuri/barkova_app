"""
Telegram bot implementation for clinic appointment management.

This module implements a Telegram bot that handles:
- Account linking/unlinking
- Appointment confirmation/cancellation
- Reminders and notifications
- User interactions via inline keyboard buttons

The bot uses long polling to receive updates from Telegram API.
"""

import json
import logging
import os
import socket
import time
from typing import Any, Dict, Optional
from urllib import error

from dotenv import load_dotenv

# IPv4-first DNS resolution for Telegram API compatibility
_original_getaddrinfo = socket.getaddrinfo


def _ipv4_first_getaddrinfo(
    host: str, port: int, family: int = 0, type: int = 0, proto: int = 0, flags: int = 0
) -> Any:
    """Force IPv4 resolution for Telegram API."""
    if host == "api.telegram.org":
        return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    return _original_getaddrinfo(host, port, family, type, proto, flags)


socket.getaddrinfo = _ipv4_first_getaddrinfo

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://backend:8000")
API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "30"))
BOT_POLLING_TIMEOUT = int(os.getenv("BOT_POLLING_TIMEOUT", "25"))


def telegram_api(method: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Call Telegram Bot API.

    Args:
        method: API method name (e.g., 'sendMessage', 'getUpdates')
        payload: Request parameters dictionary

    Returns:
        API response as dictionary

    Raises:
        error.HTTPError: If API request fails
        json.JSONDecodeError: If response is not valid JSON
    """
    from urllib import parse, request

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = None

    if payload is not None:
        data = parse.urlencode(payload).encode("utf-8")

    req = request.Request(url, data=data, method="POST" if payload is not None else "GET")

    try:
        with request.urlopen(req, timeout=API_REQUEST_TIMEOUT) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            logger.debug(f"Telegram API call successful: {method}")
            return response_data
    except error.HTTPError as exc:
        logger.error(f"Telegram API HTTP Error {exc.code}: {exc.reason}")
        raise
    except Exception as exc:
        logger.error(f"Telegram API error: {exc}")
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
    from urllib import request

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
    chat_id: int | str,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: str = "HTML",
) -> Dict[str, Any]:
    """
    Send a text message to user.

    Args:
        chat_id: Telegram chat ID
        text: Message text. By default treated as HTML — use <b>, <i>, etc.
        reply_markup: Inline / reply keyboard.
        parse_mode: "HTML" by default. Pass "" to disable parsing.

    Returns:
        API response
    """
    payload: Dict[str, Any] = {
        "chat_id": str(chat_id),
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup is not None:
        payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)

    return telegram_api("sendMessage", payload)


def answer_callback_query(callback_query_id: str, text: str) -> Dict[str, Any]:
    """
    Answer callback query (show notification in Telegram).

    Args:
        callback_query_id: Callback query ID from button press
        text: Notification text to show user

    Returns:
        API response
    """
    return telegram_api(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_query_id,
            "text": text,
        },
    )


def edit_message_text(
    chat_id: int | str,
    message_id: int | str,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: str = "HTML",
) -> Dict[str, Any]:
    """
    Edit previously sent message text.

    Args:
        chat_id: Telegram chat ID
        message_id: Message ID to edit
        text: New message text (HTML by default)
        reply_markup: New inline keyboard
        parse_mode: "HTML" by default. Pass "" to disable.

    Returns:
        API response
    """
    payload: Dict[str, Any] = {
        "chat_id": str(chat_id),
        "message_id": str(message_id),
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup is not None:
        payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)

    return telegram_api("editMessageText", payload)


def handle_start(chat_id: int, text: str) -> None:
    """
    Handle /start command.

    Supports:
    - Plain /start: Confirm bot is connected
    - /start connect_TOKEN: Link appointment to this chat

    Args:
        chat_id: User's Telegram chat ID
        text: Command text (/start with optional parameter)
    """
    from apps.integrations.exceptions import ValidationError
    from apps.integrations.bot_utils import validate_token

    parts = text.split(" ", 1)

    # Plain /start command
    if len(parts) == 1:
        send_message(
            chat_id,
            (
                "👋  <b>Здравствуйте!</b>\n\n"
                "Я — бот <b>Барковой Елены Игоревны</b>, врача-инфекциониста.\n\n"
                "Через меня вы будете получать:\n"
                "• подтверждения и напоминания о записи\n"
                "• сообщения от врача о деталях приёма\n"
                "• возможность отмены или переноса записи\n\n"
                "━━━━━━━━━━━━━━━\n"
                "<i>Чтобы записаться на консультацию — нажмите кнопку "
                "<b>«Записаться»</b> в меню снизу или перейдите на сайт.</i>"
            ),
        )
        return

    payload = parts[1].strip()

    # /start connect_TOKEN command
    if payload.startswith("connect_"):
        token = payload.replace("connect_", "", 1)

        try:
            token = validate_token(token)

            backend_post(
                "/api/appointments/telegram/prelink/link/",
                {
                    "token": token,
                    "chat_id": str(chat_id),
                },
            )

            send_message(
                chat_id,
                (
                    "✅  <b>Telegram успешно привязан</b>\n\n"
                    "Я буду присылать вам уведомления о записи к "
                    "<b>врачу-инфекционисту Барковой Елене Игоревне</b>.\n\n"
                    "━━━━━━━━━━━━━━━\n"
                    "<b>Что будет дальше:</b>\n"
                    "1️⃣  Вы получите подтверждение записи.\n"
                    "2️⃣  За 2 часа до приёма я напомню и спрошу, сможете "
                    "ли вы присутствовать.\n"
                    "3️⃣  Отменить или перенести запись можно прямо в "
                    "этом чате.\n\n"
                    "🔔  <i>Сейчас вернитесь на сайт, чтобы завершить "
                    "запись.</i>"
                ),
            )

        except ValidationError as exc:
            logger.warning(f"Invalid token in /start command: {exc}")
            send_message(
                chat_id,
                "⚠️  <b>Ошибка: неверный токен.</b>\n\n"
                "<i>Возможно, ссылка устарела. Создайте запись на сайте "
                "заново.</i>",
            )
        except Exception:
            logger.exception(f"Error linking Telegram account for chat {chat_id}")
            send_message(
                chat_id,
                "⚠️  <b>Не удалось подключить Telegram</b>\n\n"
                "<i>Попробуйте чуть позже или вернитесь к боту "
                "по ссылке с сайта ещё раз.</i>",
            )

        return

    # Unknown /start parameter
    send_message(
        chat_id,
        "🤔  <i>Команда распознана, но сценарий не найден. "
        "Попробуйте начать с кнопки «Записаться».</i>",
    )


def _public_url(path: str = "/") -> str:
    """Сборка публичной URL'и сайта (для Web App кнопок)."""
    base = os.getenv("PUBLIC_BASE_URL", "https://doctor-barkova.ru").rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return f"{base}{path}"


def handle_book(chat_id: int) -> None:
    """Команда /book — открывает Mini App записи."""
    send_message(
        chat_id,
        (
            "📅  <b>Запись на консультацию</b>\n\n"
            "Нажмите кнопку ниже — откроется удобная форма записи прямо "
            "здесь, в Telegram."
        ),
        reply_markup={
            "inline_keyboard": [
                [
                    {
                        "text": "📅  Открыть запись",
                        "web_app": {"url": _public_url("/booking?tg=1")},
                    }
                ]
            ]
        },
    )


def handle_my_appointments(chat_id: int) -> None:
    """Команда /myappointments — открывает Mini App со списком записей."""
    appointment = find_active_appointment_for_chat(chat_id)
    if not appointment:
        send_message(
            chat_id,
            (
                "📭  <b>У вас нет активных записей</b>\n\n"
                "<i>Нажмите кнопку «Записаться» в меню, чтобы создать новую.</i>"
            ),
        )
        return

    slot = appointment.slot
    send_message(
        chat_id,
        (
            "📋  <b>Ваша запись</b>\n\n"
            f"📅  <b>{slot.date.strftime('%d.%m.%Y')}</b>\n"
            f"🕐  <b>{slot.start_time.strftime('%H:%M')} – "
            f"{slot.end_time.strftime('%H:%M')}</b>\n"
            f"📌  Статус: <i>{appointment.get_status_display()}</i>"
        ),
        reply_markup={
            "inline_keyboard": [
                [
                    {
                        "text": "📅  Перенести",
                        "web_app": {
                            "url": _public_url(
                                f"/booking?tg=1&reschedule={appointment.id}"
                            )
                        },
                    },
                    {
                        "text": "❌  Отменить",
                        "callback_data": f"cancel:{appointment.id}:_",
                    },
                ]
            ]
        },
    )


def handle_help(chat_id: int) -> None:
    """Команда /help — справка."""
    send_message(
        chat_id,
        (
            "ℹ️  <b>Справка</b>\n\n"
            "Через этого бота вы можете:\n\n"
            "📅  <b>/book</b> — записаться на онлайн-консультацию\n"
            "📋  <b>/myappointments</b> — посмотреть свои записи\n"
            "👋  <b>/start</b> — приветствие и главное меню\n\n"
            "━━━━━━━━━━━━━━━\n"
            "<i>Если возникли вопросы — просто напишите сообщение в этот "
            "чат, врач или администратор ответит.</i>"
        ),
    )


def handle_callback(callback_query: Dict[str, Any]) -> None:
    """
    Handle inline button callback.

    Expected callback_data format: "action:appointment_id:token"
    Supported actions: confirm, cancel, keep, yes, no, doctor

    Args:
        callback_query: Callback query dict from Telegram API
    """
    from apps.integrations.exceptions import CallbackDataError
    from apps.integrations.bot_utils import parse_callback_data

    callback_query_id = callback_query.get("id", "")
    data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if not all([callback_query_id, chat_id, message_id]):
        logger.warning("Invalid callback_query structure")
        return

    # Parse callback data
    try:
        callback_data = parse_callback_data(data, separator=":")
        action = callback_data.get("action")
        appointment_id = callback_data.get("appointment_id")
        token = callback_data.get("token")
    except CallbackDataError as exc:
        logger.warning(f"Failed to parse callback data: {exc}")
        answer_callback_query(callback_query_id, "Некорректная команда.")
        return

    # Validate action
    allowed_actions = {"confirm", "cancel", "keep", "yes", "no", "doctor"}
    if action not in allowed_actions:
        logger.warning(f"Unknown action in callback: {action}")
        answer_callback_query(callback_query_id, "Неизвестное действие.")
        return

    # Handle "keep" action locally
    if action == "keep":
        answer_callback_query(callback_query_id, "Запись оставлена без изменений.")
        edit_message_text(chat_id, message_id, "✅ Запись оставлена без изменений")
        return

    # Send action to backend
    try:
        backend_post(
            "/api/appointments/telegram/action/",
            {
                "appointment_id": appointment_id,
                "token": token,
                "action": action,
                "chat_id": str(chat_id),
            },
        )

        # Provide user feedback
        feedback_messages = {
            "confirm": ("Запись подтверждена.", "✅ Запись подтверждена"),
            "cancel": ("Запись отменена.", "❌ Запись отменена"),
            "yes": ("Отлично, ждём вас.", "✅ Вы подтвердили, что сможете прийти"),
            "no": ("Запись отменена.", "❌ Вы сообщили, что не сможете прийти"),
            "doctor": ("Передали врачу.", "💬 Запрос на связь с врачом передан"),
        }

        notification, edit_text = feedback_messages.get(action, ("Готово", "✅ Готово"))

        answer_callback_query(callback_query_id, notification)
        edit_message_text(chat_id, message_id, edit_text)

    except Exception as exc:
        logger.exception(f"Error processing callback action {action} for appointment {appointment_id}")
        answer_callback_query(callback_query_id, f"Ошибка: {str(exc)[:100]}")


def find_active_appointment_for_chat(chat_id: int | str) -> Optional[Any]:
    """
    Find active appointment for Telegram user.

    Args:
        chat_id: Telegram chat ID

    Returns:
        Appointment object or None if not found
    """
    from apps.integrations.bot_utils import get_appointment_by_user

    try:
        return get_appointment_by_user(chat_id, "telegram")
    except Exception as exc:
        logger.error(f"Failed to find appointment for chat {chat_id}: {exc}")
        return None


def send_cancel_confirmation(chat_id: int | str, appointment: Any) -> Dict[str, Any]:
    """
    Send cancellation confirmation prompt to user.

    Args:
        chat_id: Telegram chat ID
        appointment: Appointment object with related slot

    Returns:
        API response
    """
    slot = appointment.slot
    date_str = slot.date.strftime("%d.%m.%Y")
    time_str = f"{slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}"

    return telegram_api(
        "sendMessage",
        {
            "chat_id": str(chat_id),
            "text": (
                "Вы хотите отменить запись?\n"
                f"📅 Дата: {date_str}\n"
                f"🕐 Время: {time_str}"
            ),
            "reply_markup": json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Подтвердить отмену",
                                "callback_data": f"cancel:{appointment.id}:{appointment.telegram_link_token}",
                            },
                            {
                                "text": "Оставить запись",
                                "callback_data": f"keep:{appointment.id}:{appointment.telegram_link_token}",
                            },
                        ]
                    ]
                },
                ensure_ascii=False,
            ),
        },
    )


def main() -> None:
    """
    Start bot's main polling loop.

    This function:
    1. Initializes Django ORM
    2. Starts long polling for Telegram updates
    3. Handles all incoming messages and callbacks
    4. Implements error recovery with exponential backoff
    """
    from apps.integrations.base_bot import BaseBot

    # Initialize Django once
    BaseBot.setup_django()

    offset: Optional[int] = None
    retry_count = 0
    max_retries = 5

    logger.info("Telegram bot started")

    while True:
        try:
            payload = {"timeout": BOT_POLLING_TIMEOUT}
            if offset is not None:
                payload["offset"] = offset

            data = telegram_api("getUpdates", payload)

            for item in data.get("result", []):
                try:
                    offset = item.get("update_id", 0) + 1

                    # Handle callback from button press
                    if "callback_query" in item:
                        handle_callback(item["callback_query"])
                        continue

                    # Handle regular message
                    message = item.get("message")
                    if not message:
                        continue

                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    text = message.get("text", "")

                    if not chat_id:
                        logger.warning("Message without chat_id")
                        continue

                    # Handle /start command
                    if text.startswith("/start"):
                        handle_start(chat_id, text)

                    elif text.startswith("/book"):
                        handle_book(chat_id)

                    elif text.startswith("/myappointments") or text.startswith("/my_appointments"):
                        handle_my_appointments(chat_id)

                    elif text.startswith("/help"):
                        handle_help(chat_id)

                    # Handle regular messages (check for cancel request)
                    elif text.strip():
                        appointment = find_active_appointment_for_chat(chat_id)
                        if appointment:
                            send_cancel_confirmation(chat_id, appointment)
                        else:
                            send_message(
                                chat_id,
                                "📭  <b>У вас нет активной записи</b>\n\n"
                                "<i>Чтобы записаться на консультацию — "
                                "нажмите кнопку «Записаться» в меню снизу.</i>",
                            )

                except Exception as exc:
                    logger.exception(f"Error processing update {item.get('update_id')}")

            # Reset retry counter on success
            retry_count = 0

        except error.HTTPError as exc:
            retry_count += 1
            logger.error(f"Telegram API HTTP Error {exc.code} (retry {retry_count}/{max_retries})")
            wait_time = min(2**retry_count, 60)  # Exponential backoff, max 60 seconds
            time.sleep(wait_time)

        except Exception as exc:
            retry_count += 1
            logger.exception(f"Telegram polling error (retry {retry_count}/{max_retries})")
            wait_time = min(2**retry_count, 60)  # Exponential backoff, max 60 seconds
            time.sleep(wait_time)

            if retry_count >= max_retries:
                logger.critical(f"Max retries ({max_retries}) exceeded, restarting bot")
                retry_count = 0


if __name__ == "__main__":
    main()

import json
import mimetypes
import os
import time
from urllib import error, parse, request

from django.conf import settings
from django.utils import timezone

from .models import NotificationLog

from .vk_constants import (
    VK_CMD_MANAGE,
    VK_CMD_CONFIRM,
    VK_CMD_CANCEL_REQUEST,
    VK_CMD_YES,
    VK_CMD_DOCTOR,
)


# =========================
# Telegram
# =========================

def _telegram_is_configured() -> bool:
    return bool(
        getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        and getattr(settings, "TELEGRAM_CHAT_ID", "")
    )


def _telegram_api_url(method: str) -> str:
    token = settings.TELEGRAM_BOT_TOKEN
    return f"https://api.telegram.org/bot{token}/{method}"


def _send_telegram_text_custom(text: str, chat_id: str) -> tuple[bool, str, str]:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return False, "", "Telegram is not configured"

    url = _telegram_api_url("sendMessage")
    payload = parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
    ).encode("utf-8")

    req = request.Request(url, data=payload, method="POST")

    try:
        with request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)

        if not data.get("ok"):
            return False, "", json.dumps(data, ensure_ascii=False)

        result = data.get("result", {})
        message_id = str(result.get("message_id", ""))
        return True, message_id, ""

    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return False, "", f"HTTPError {exc.code}: {body}"
    except Exception as exc:
        return False, "", str(exc)


def _send_telegram_text(text: str) -> tuple[bool, str, str]:
    if not _telegram_is_configured():
        return False, "", "Telegram is not configured"

    return _send_telegram_text_custom(text=text, chat_id=settings.TELEGRAM_CHAT_ID)


def _send_telegram_text_with_keyboard_custom(
    text: str,
    chat_id: str,
    reply_markup: dict,
) -> tuple[bool, str, str]:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return False, "", "Telegram is not configured"

    url = _telegram_api_url("sendMessage")
    payload = parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(reply_markup, ensure_ascii=False),
        }
    ).encode("utf-8")

    req = request.Request(url, data=payload, method="POST")

    try:
        with request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)

        if not data.get("ok"):
            return False, "", json.dumps(data, ensure_ascii=False)

        result = data.get("result", {})
        message_id = str(result.get("message_id", ""))
        return True, message_id, ""

    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return False, "", f"HTTPError {exc.code}: {body}"
    except Exception as exc:
        return False, "", str(exc)


def _send_telegram_file(file_path: str, chat_id: str, caption: str = "") -> tuple[bool, str, str]:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return False, "", "Telegram is not configured"

    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(filename)
    mime_type = mime_type or "application/octet-stream"

    is_image = mime_type.startswith("image/")
    method = "sendPhoto" if is_image else "sendDocument"
    file_field = "photo" if is_image else "document"

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()

    def add_text_field(name: str, value: str):
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(f"{value}\r\n".encode())

    add_text_field("chat_id", str(chat_id))
    if caption:
        add_text_field("caption", caption)
        add_text_field("parse_mode", "HTML")

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode()
    )
    body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode())

    with open(file_path, "rb") as f:
        body.extend(f.read())

    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    req = request.Request(
        _telegram_api_url(method),
        data=bytes(body),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    try:
        with request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)

        if not data.get("ok"):
            return False, "", json.dumps(data, ensure_ascii=False)

        result = data.get("result", {})
        message_id = str(result.get("message_id", ""))
        return True, message_id, ""

    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return False, "", f"HTTPError {exc.code}: {body}"
    except Exception as exc:
        return False, "", str(exc)


# =========================
# VK
# =========================

def _vk_is_configured() -> bool:
    return bool(
        getattr(settings, "VK_GROUP_TOKEN", "")
        and getattr(settings, "VK_GROUP_ID", "")
    )


def _vk_api_url(method: str) -> str:
    return f"https://api.vk.com/method/{method}"


def _vk_request(method: str, payload: dict) -> tuple[bool, dict, str]:
    token = getattr(settings, "VK_GROUP_TOKEN", "")
    if not token:
        return False, {}, "VK is not configured"

    data = {
        **payload,
        "access_token": token,
        "v": "5.199",
    }

    encoded = parse.urlencode(data).encode("utf-8")
    req = request.Request(_vk_api_url(method), data=encoded, method="POST")

    try:
        with request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)

        if "error" in result:
            return False, result, json.dumps(result, ensure_ascii=False)

        return True, result, ""
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return False, {}, f"HTTPError {exc.code}: {body}"
    except Exception as exc:
        return False, {}, str(exc)

def _vk_peer_for_appointment(appointment):
    if getattr(appointment, "vk_peer_id", None):
        return str(appointment.vk_peer_id)

    if getattr(appointment, "vk_user_id", None):
        return str(appointment.vk_user_id)

    return ""

def _vk_user_for_appointment(appointment):
    if getattr(appointment, "vk_user_id", None):
        return str(appointment.vk_user_id)
    return ""


def _vk_is_messages_allowed(user_id: str) -> tuple[bool, str]:
    if not _vk_is_configured() or not user_id:
        return False, "VK user id is missing"

    success, result, error_text = _vk_request(
        "messages.isMessagesFromGroupAllowed",
        {
            "group_id": settings.VK_GROUP_ID,
            "user_id": str(user_id),
        },
    )

    if not success:
        return False, error_text

    response = result.get("response", {})
    is_allowed = bool(response.get("is_allowed"))
    return is_allowed, ""


def _send_vk_text_custom(text: str, peer_id: str) -> tuple[bool, str, str]:
    if not _vk_is_configured() or not peer_id:
        return False, "", "VK is not configured"

    success, result, error_text = _vk_request(
        "messages.send",
        {
            "peer_id": str(peer_id),
            "message": text,
            "random_id": int(time.time() * 1000),
        },
    )

    if not success:
        return False, "", error_text

    message_id = str(result.get("response", ""))
    return True, message_id, ""


def _send_vk_text_with_keyboard_custom(text: str, peer_id: str, keyboard: dict) -> tuple[bool, str, str]:
    if not _vk_is_configured() or not peer_id:
        return False, "", "VK is not configured"

    success, result, error_text = _vk_request(
        "messages.send",
        {
            "peer_id": str(peer_id),
            "message": text,
            "keyboard": json.dumps(keyboard, ensure_ascii=False),
            "random_id": int(time.time() * 1000),
        },
    )

    if not success:
        return False, "", error_text

    message_id = str(result.get("response", ""))
    return True, message_id, ""


# =========================
# Common formatters
# =========================

def _format_appointment_created_text(appointment) -> str:
    slot = appointment.slot
    reason = appointment.reason.strip() if appointment.reason else "Не указана"
    contact_method = appointment.preferred_contact_method or "не указан"

    return (
        "<b>Новая запись</b>\n"
        f"Пациент: {appointment.name}\n"
        f"Телефон: {appointment.phone}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Причина: {reason}\n"
        f"Способ связи: {contact_method}\n"
        f"Telegram: {appointment.telegram_username or '—'}\n"
        f"Статус: {appointment.get_status_display()}"
    )


def _format_appointment_status_text(appointment) -> str:
    slot = appointment.slot
    return (
        "<b>Изменение статуса записи</b>\n"
        f"Пациент: {appointment.name}\n"
        f"Телефон: {appointment.phone}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Новый статус: {appointment.get_status_display()}"
    )


# =========================
# Telegram public helpers
# =========================

def send_to_patient(appointment, text):
    if not appointment.telegram_chat_id:
        return False, "", "Telegram chat_id отсутствует"

    return _send_telegram_text_custom(
        text=text,
        chat_id=appointment.telegram_chat_id,
    )


def send_created_message_to_patient_with_actions(appointment):
    if not appointment.telegram_chat_id:
        return

    text = (
        "✅ Вы записаны на онлайн-консультацию\n"
        f"Дата: {appointment.slot.date}\n"
        f"Время: {appointment.slot.start_time.strftime('%H:%M')}–{appointment.slot.end_time.strftime('%H:%M')}\n\n"
        "Пожалуйста, подтвердите запись кнопкой ниже.\n"
        "Если планы изменятся или консультация больше не нужна, вы сможете отменить запись кнопкой ниже "
        "или просто написать сообщение в этот чат."
    )

    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "Подтвердить",
                    "callback_data": f"confirm:{appointment.id}:{appointment.telegram_link_token}",
                },
                {
                    "text": "Отменить",
                    "callback_data": f"cancel:{appointment.id}:{appointment.telegram_link_token}",
                },
            ]
        ]
    }

    _send_telegram_text_with_keyboard_custom(
        text=text,
        chat_id=appointment.telegram_chat_id,
        reply_markup=reply_markup,
    )

def send_reminder_with_actions_telegram(appointment):
    if not appointment.telegram_chat_id:
        return False, "", "Нет chat_id"

    text = (
        "⏰ Напоминание о консультации\n"
        f"Сегодня консультация через 2 часа\n\n"
        f"Дата: {appointment.slot.date}\n"
        f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
        f"{appointment.slot.end_time.strftime('%H:%M')}\n\n"
        "Сможете присутствовать?"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ Смогу",
                    "callback_data": f"yes:{appointment.id}:{appointment.telegram_link_token}",
                },
                {
                    "text": "❌ Не смогу",
                    "callback_data": f"no:{appointment.id}:{appointment.telegram_link_token}",
                },
            ],
            [
                {
                    "text": "💬 Связь с врачом",
                    "callback_data": f"doctor:{appointment.id}:{appointment.telegram_link_token}",
                }
            ],
        ]
    }

    return _send_telegram_text_with_keyboard_custom(
        text=text,
        chat_id=appointment.telegram_chat_id,
        reply_markup=keyboard,
    )

# =========================
# VK public helpers
# =========================

def send_to_patient_vk(appointment, text, keyboard: dict | None = None):
    peer_id = _vk_peer_for_appointment(appointment)
    user_id = _vk_user_for_appointment(appointment)

    if not peer_id or not user_id:
        return False, "", "VK peer_id или user_id отсутствует"

    allowed, allowed_error = _vk_is_messages_allowed(user_id)
    if not allowed:
        return False, "", allowed_error or "Пользователь не разрешил сообщения от сообщества"

    if keyboard is not None:
        success, message_id, error_text = _send_vk_text_with_keyboard_custom(
            text=text,
            peer_id=peer_id,
            keyboard=keyboard,
        )
    else:
        success, message_id, error_text = _send_vk_text_custom(
            text=text,
            peer_id=peer_id,
        )

    return success, message_id, error_text


def get_vk_remove_keyboard():
    return {
        "one_time": False,
        "inline": False,
        "buttons": [],
    }


def build_vk_new_appointment_keyboard(appointment):
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
                                "cmd": VK_CMD_CONFIRM,
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
                                "cmd": VK_CMD_CANCEL_REQUEST,
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


def build_vk_reminder_keyboard(appointment):
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "label": "Смогу",
                        "payload": json.dumps(
                            {
                                "cmd": VK_CMD_YES,
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
                        "label": "Не смогу",
                        "payload": json.dumps(
                            {
                                "cmd": VK_CMD_CANCEL_REQUEST,
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "negative",
                },
            ],
            [
                {
                    "action": {
                        "type": "callback",
                        "label": "Связь с врачом",
                        "payload": json.dumps(
                            {
                                "cmd": VK_CMD_DOCTOR,
                                "appointment_id": appointment.id,
                                "token": appointment.vk_link_token,
                            },
                            ensure_ascii=False,
                        ),
                    },
                    "color": "primary",
                }
            ],
        ],
    }


def build_vk_booking_keyboard():
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "open_link",
                        "label": "Записаться онлайн",
                        "link": "https://doctor-barkova.ru/booking",
                    }
                }
            ]
        ],
    }


def build_vk_active_root_keyboard(appointment):
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
                                "cmd": VK_CMD_MANAGE,
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


def build_vk_manage_keyboard(appointment):
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
                                "cmd": VK_CMD_CANCEL_REQUEST,
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
                                "cmd": VK_CMD_DOCTOR,
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


def send_created_message_to_patient_with_actions_vk(appointment):
    text = (
        "✅ Вы записаны на онлайн-консультацию\n"
        f"Дата: {appointment.slot.date}\n"
        f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
        f"{appointment.slot.end_time.strftime('%H:%M')}\n\n"
        "Пожалуйста, подтвердите запись кнопкой ниже."
    )

    return send_to_patient_vk(
        appointment,
        text,
        keyboard=build_vk_new_appointment_keyboard(appointment),
    )


def send_reminder_with_actions_vk(appointment):
    text = (
        "⏰ Напоминание о консультации\n"
        "Сегодня консультация через 2 часа.\n\n"
        f"Дата: {appointment.slot.date}\n"
        f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
        f"{appointment.slot.end_time.strftime('%H:%M')}\n\n"
        "Сможете присутствовать?"
    )

    return send_to_patient_vk(
        appointment,
        text,
        keyboard=build_vk_reminder_keyboard(appointment),
    )

# =========================
# Doctor notifications
# =========================

def send_appointment_created_notification(appointment) -> None:
    text = _format_appointment_created_text(appointment)

    log = NotificationLog.objects.create(
        appointment=appointment,
        channel="telegram",
        notification_type="created",
        status="pending",
        payload={"text": text},
    )

    success, external_message_id, error_text = _send_telegram_text(text)

    attachment_errors = []
    if success:
        for index, attachment in enumerate(appointment.attachments.all(), start=1):
            caption = f"Файл пациента {index}" if index == 1 else ""
            file_success, _, file_error = _send_telegram_file(
                attachment.file.path,
                settings.TELEGRAM_CHAT_ID,
                caption=caption,
            )
            if not file_success:
                attachment_errors.append(f"{attachment.file.name}: {file_error}")

    if success and not attachment_errors:
        log.status = "sent"
        log.external_message_id = external_message_id
        log.sent_at = timezone.now()
        log.error_text = ""
    elif success and attachment_errors:
        log.status = "failed"
        log.external_message_id = external_message_id
        log.sent_at = timezone.now()
        log.error_text = " ; ".join(attachment_errors)
    else:
        log.status = "failed"
        log.error_text = error_text

    log.save(update_fields=["status", "external_message_id", "sent_at", "error_text"])


def send_appointment_status_notification(appointment) -> None:
    status_to_type = {
        "confirmed": "confirmed",
        "cancelled": "cancelled",
    }

    notification_type = status_to_type.get(appointment.status)
    if not notification_type:
        return

    text = _format_appointment_status_text(appointment)

    log = NotificationLog.objects.create(
        appointment=appointment,
        channel="telegram",
        notification_type=notification_type,
        status="pending",
        payload={"text": text},
    )

    success, external_message_id, error_text = _send_telegram_text(text)

    if success:
        log.status = "sent"
        log.external_message_id = external_message_id
        log.sent_at = timezone.now()
        log.error_text = ""
    else:
        log.status = "failed"
        log.error_text = error_text

    log.save(update_fields=["status", "external_message_id", "sent_at", "error_text"])

def send_doctor_contact_request_notification(appointment) -> None:
    text = (
        "<b>Пациент просит связаться</b>\n"
        f"Пациент: {appointment.name}\n"
        f"Телефон: {appointment.phone}\n"
        f"Дата: {appointment.slot.date}\n"
        f"Время: {appointment.slot.start_time.strftime('%H:%M')}–{appointment.slot.end_time.strftime('%H:%M')}\n"
        f"Способ связи: {appointment.preferred_contact_method or 'не указан'}"
    )

    log = NotificationLog.objects.create(
        appointment=appointment,
        channel="telegram",
        notification_type="doctor_contact",
        status="pending",
        payload={"text": text},
    )

    success, external_message_id, error_text = _send_telegram_text(text)

    if success:
        log.status = "sent"
        log.external_message_id = external_message_id
        log.sent_at = timezone.now()
        log.error_text = ""
    else:
        log.status = "failed"
        log.error_text = error_text

    log.save(update_fields=["status", "external_message_id", "sent_at", "error_text"])

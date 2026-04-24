"""
Notifiers — высокоуровневый слой отправки уведомлений.

Использует:
  transports/telegram.py  — низкоуровневые HTTP-вызовы Telegram
  transports/vk.py        — низкоуровневые HTTP-вызовы VK
  keyboards/telegram.py   — Telegram inline-клавиатуры
  keyboards/vk.py         — VK callback-клавиатуры
  messages/doctor.py      — форматтеры сообщений врача
  messages/patient.py     — форматтеры сообщений пациента
"""
from __future__ import annotations

import logging

from django.utils import timezone

from .models import NotificationLog
from .transports import telegram as tg
from .transports import vk as vk_transport
from .keyboards import telegram as tg_kb
from .keyboards import vk as vk_kb
from .messages import doctor as doctor_msg
from .messages import patient as patient_msg

logger = logging.getLogger("apps.notifications.notifiers")


# ─── helpers ──────────────────────────────────────────────────────────────────

def _save_log(log: NotificationLog, success: bool, message_id: str, error_text: str) -> None:
    if success:
        log.status = "sent"
        log.external_message_id = message_id
        log.sent_at = timezone.now()
        log.error_text = ""
    else:
        log.status = "failed"
        log.error_text = error_text
    log.save(update_fields=["status", "external_message_id", "sent_at", "error_text"])


# ─── Patient helpers ───────────────────────────────────────────────────────────

def send_to_patient(appointment, text: str, keyboard: dict | None = None) -> tuple[bool, str, str]:
    """Отправляет произвольный текст пациенту в Telegram."""
    if not appointment.telegram_chat_id:
        return False, "", "Telegram chat_id отсутствует"
    return tg.send_message(
        chat_id=appointment.telegram_chat_id,
        text=text,
        reply_markup=keyboard,
    )


def send_to_patient_vk(appointment, text: str, keyboard: dict | None = None) -> tuple[bool, str, str]:
    """Отправляет произвольный текст пациенту в VK."""
    peer_id = getattr(appointment, "vk_peer_id", None) or getattr(appointment, "vk_user_id", None)
    user_id = getattr(appointment, "vk_user_id", None)

    if not peer_id or not user_id:
        return False, "", "VK peer_id или user_id отсутствует"

    allowed, allowed_error = vk_transport.is_messages_allowed(str(user_id))
    if not allowed:
        return False, "", allowed_error or "Пользователь не разрешил сообщения от сообщества"

    return vk_transport.send_message(peer_id=str(peer_id), text=text, keyboard=keyboard)


# ─── Doctor notifications ──────────────────────────────────────────────────────

def send_appointment_created_notification(appointment) -> None:
    """Уведомляет врача о новой записи (текст + вложения)."""
    text = doctor_msg.appointment_created(appointment)
    log = NotificationLog.objects.create(
        appointment=appointment,
        channel="telegram",
        notification_type="created",
        status="pending",
        payload={"text": text},
    )

    success, message_id, error_text = tg.send_to_doctor(text)

    attachment_errors: list[str] = []
    if success:
        for idx, attachment in enumerate(appointment.attachments.all(), start=1):
            caption = f"Файл пациента {idx}" if idx == 1 else ""
            ok, _, file_err = tg.send_file(
                attachment.file.path,
                settings_chat_id(),
                caption=caption,
            )
            if not ok:
                attachment_errors.append(f"{attachment.file.name}: {file_err}")

    if success and attachment_errors:
        error_text = " ; ".join(attachment_errors)
        success = False

    _save_log(log, success, message_id, error_text)


def send_appointment_status_notification(appointment) -> None:
    """Уведомляет врача об изменении статуса записи."""
    status_to_type = {"confirmed": "confirmed", "cancelled": "cancelled"}
    notification_type = status_to_type.get(appointment.status)
    if not notification_type:
        return

    text = doctor_msg.appointment_status_changed(appointment)
    log = NotificationLog.objects.create(
        appointment=appointment,
        channel="telegram",
        notification_type=notification_type,
        status="pending",
        payload={"text": text},
    )
    success, message_id, error_text = tg.send_to_doctor(text)
    _save_log(log, success, message_id, error_text)


def send_doctor_contact_request_notification(appointment) -> None:
    """Уведомляет врача, что пациент просит связаться."""
    text = doctor_msg.contact_requested(appointment)
    log = NotificationLog.objects.create(
        appointment=appointment,
        channel="telegram",
        notification_type="doctor_contact",
        status="pending",
        payload={"text": text},
    )
    success, message_id, error_text = tg.send_to_doctor(text)
    _save_log(log, success, message_id, error_text)


# ─── Patient notifications ─────────────────────────────────────────────────────

def send_created_message_to_patient_with_actions(appointment) -> None:
    """Сообщение пациенту о новой записи (Telegram) с кнопками."""
    if not appointment.telegram_chat_id:
        return
    send_to_patient(
        appointment,
        patient_msg.booking_created(appointment),
        keyboard=tg_kb.new_appointment(appointment),
    )


def send_created_message_to_patient_with_actions_vk(appointment) -> tuple:
    """Сообщение пациенту о новой записи (VK) с кнопками."""
    return send_to_patient_vk(
        appointment,
        patient_msg.booking_created_vk(appointment),
        keyboard=vk_kb.new_appointment(appointment),
    )


def send_reminder_with_actions_telegram(appointment) -> tuple:
    """Напоминание пациенту в Telegram с кнопками."""
    if not appointment.telegram_chat_id:
        return False, "", "Нет chat_id"
    return send_to_patient(
        appointment,
        patient_msg.reminder(appointment),
        keyboard=tg_kb.reminder(appointment),
    )


def send_reminder_with_actions_vk(appointment) -> tuple:
    """Напоминание пациенту в VK с кнопками."""
    return send_to_patient_vk(
        appointment,
        patient_msg.reminder(appointment),
        keyboard=vk_kb.reminder(appointment),
    )


# ─── VK keyboard helpers (публичный API для views/vk_bot) ─────────────────────

def get_vk_remove_keyboard() -> dict:
    return vk_kb.remove()


def build_vk_new_appointment_keyboard(appointment) -> dict:
    return vk_kb.new_appointment(appointment)


def build_vk_reminder_keyboard(appointment) -> dict:
    return vk_kb.reminder(appointment)


def build_vk_booking_keyboard() -> dict:
    return vk_kb.booking()


def build_vk_active_root_keyboard(appointment) -> dict:
    return vk_kb.active_root(appointment)


def build_vk_manage_keyboard(appointment) -> dict:
    return vk_kb.manage(appointment)


# ─── VK messaging check (публичный API для views) ─────────────────────────────

def _vk_is_messages_allowed(user_id: str) -> tuple[bool, str]:
    return vk_transport.is_messages_allowed(user_id)


# ─── internal util ────────────────────────────────────────────────────────────

def settings_chat_id() -> str:
    from django.conf import settings as _s
    return _s.TELEGRAM_CHAT_ID

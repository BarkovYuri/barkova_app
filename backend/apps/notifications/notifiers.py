"""
Notifiers — высокоуровневая отправка уведомлений.

Врачу: личные сообщения VK от сообщества на аккаунты из VK_DOCTOR_USER_IDS,
при неудаче резервное письмо на DOCTOR_ALERT_EMAILS.
Пациенту: сообщения VK от сообщества.

Каждая отправка пишется в NotificationLog, чтобы сбои было видно в админке.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .keyboards import vk as vk_kb
from .messages import doctor as doctor_msg
from .messages import patient as patient_msg
from .models import NotificationLog
from .transports import vk as vk_transport

logger = logging.getLogger("apps.notifications.notifiers")


def _log(
    *,
    channel: str,
    notification_type: str,
    recipient: str,
    text: str,
    success: bool,
    message_id: str = "",
    error_text: str = "",
    appointment=None,
) -> NotificationLog:
    return NotificationLog.objects.create(
        appointment=appointment,
        channel=channel,
        notification_type=notification_type,
        recipient=str(recipient)[:255],
        status="sent" if success else "failed",
        external_message_id=message_id,
        payload={"text": text[:4000]},
        error_text=error_text[:4000],
        sent_at=timezone.now() if success else None,
    )


# ─── Врачу ────────────────────────────────────────────────────────────────────


def _email_doctor(text: str, *, notification_type: str, appointment=None) -> bool:
    emails = list(getattr(settings, "DOCTOR_ALERT_EMAILS", []) or [])
    if not emails:
        return False
    subject = (text.splitlines() or ["Оповещение сайта"])[0][:150]
    try:
        send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)
    except Exception as exc:
        logger.exception("Doctor email alert failed")
        _log(
            channel="email",
            notification_type=notification_type,
            recipient=",".join(emails),
            text=text,
            success=False,
            error_text=str(exc),
            appointment=appointment,
        )
        return False
    _log(
        channel="email",
        notification_type=notification_type,
        recipient=",".join(emails),
        text=text,
        success=True,
        appointment=appointment,
    )
    return True


def alert_doctor(
    text: str,
    *,
    notification_type: str,
    appointment=None,
    email_fallback: bool = True,
) -> bool:
    """
    Отправляет алерт врачу. True, если хотя бы один получатель его получил.

    email_fallback=False используют Celery-задачи на промежуточных
    попытках: письмо уходит только когда VK не сработал окончательно.
    """
    delivered = False
    for user_id in getattr(settings, "VK_DOCTOR_USER_IDS", []) or []:
        ok, message_id, error_text = vk_transport.send_message(user_id, text)
        _log(
            channel="vk",
            notification_type=notification_type,
            recipient=f"vk:{user_id}",
            text=text,
            success=ok,
            message_id=message_id,
            error_text=error_text,
            appointment=appointment,
        )
        delivered = delivered or ok

    if not delivered and email_fallback:
        delivered = _email_doctor(text, notification_type=notification_type, appointment=appointment)

    if not delivered:
        logger.error("Doctor alert '%s' was not delivered to any channel", notification_type)
        no_channels = not getattr(settings, "VK_DOCTOR_USER_IDS", []) and not getattr(
            settings, "DOCTOR_ALERT_EMAILS", []
        )
        if no_channels and email_fallback:
            # Без получателей отправлять некуда. Фиксируем это в логе, чтобы
            # проблема была видна в админке, а не только в логах сервера.
            _log(
                channel="vk",
                notification_type=notification_type,
                recipient="не настроено",
                text=text,
                success=False,
                error_text="Не заданы VK_DOCTOR_USER_IDS и DOCTOR_ALERT_EMAILS",
                appointment=appointment,
            )
    return delivered


def doctor_alert_sent(appointment, notification_type: str) -> bool:
    return NotificationLog.objects.filter(
        appointment=appointment, notification_type=notification_type, status="sent"
    ).exists()


# ─── Пациенту ─────────────────────────────────────────────────────────────────


def send_to_patient_vk(
    appointment,
    text: str,
    keyboard: dict | None = None,
    *,
    notification_type: str = "",
) -> tuple[bool, str, str]:
    """Отправляет произвольный текст пациенту в VK. Возвращает (ok, message_id, error)."""
    peer_id = appointment.vk_peer_id or appointment.vk_user_id
    if not peer_id or not appointment.vk_user_id:
        return False, "", "VK пациента не привязан"

    ok, message_id, error_text = vk_transport.send_message(peer_id=peer_id, text=text, keyboard=keyboard)
    if notification_type:
        _log(
            channel="vk",
            notification_type=notification_type,
            recipient=f"vk:{peer_id}",
            text=text,
            success=ok,
            message_id=message_id,
            error_text=error_text,
            appointment=appointment,
        )
    return ok, message_id, error_text


def send_booking_created_to_patient(appointment) -> tuple[bool, str]:
    """
    Сообщение «вы записаны» с кнопками. Возвращает (ok, error_text).

    Если сообщество пока не может писать пациенту, ничего не логируем как
    ошибку: сообщение уйдёт, когда пациент напишет в сообщество или
    разрешит сообщения (см. vk_bot).
    """
    if appointment.patient_notified_at:
        return True, ""
    allowed, error_text = vk_transport.is_messages_allowed(appointment.vk_user_id)
    if not allowed:
        return False, error_text or "not_allowed"

    ok, _, error_text = send_to_patient_vk(
        appointment,
        patient_msg.booking_created(appointment),
        keyboard=vk_kb.new_appointment(appointment),
        notification_type="patient_created",
    )
    if ok:
        type(appointment).objects.filter(pk=appointment.pk, patient_notified_at__isnull=True).update(
            patient_notified_at=timezone.now()
        )
        appointment.patient_notified_at = timezone.now()
    return ok, error_text


def send_reminder_to_patient(appointment) -> tuple[bool, str]:
    ok, _, error_text = send_to_patient_vk(
        appointment,
        patient_msg.reminder(appointment),
        keyboard=vk_kb.reminder(appointment),
        notification_type="reminder",
    )
    return ok, error_text


def send_status_to_patient(appointment, status: str) -> tuple[bool, str]:
    """Пациенту: врач подтвердил или отменил запись."""
    if status == "confirmed":
        text, keyboard = patient_msg.confirmed_by_doctor(appointment), vk_kb.active_root(appointment)
    elif status == "cancelled":
        text, keyboard = patient_msg.cancelled_by_doctor(appointment), vk_kb.booking()
    else:
        return True, ""
    ok, _, error_text = send_to_patient_vk(appointment, text, keyboard=keyboard, notification_type="patient_status")
    return ok, error_text


# ─── Тексты алертов врачу (обёртки для задач) ─────────────────────────────────


def new_appointment_alert_text(appointment) -> str:
    reachable: bool | None = None
    if appointment.vk_user_id:
        reachable, _ = vk_transport.is_messages_allowed(appointment.vk_user_id)
    return doctor_msg.appointment_created(
        appointment,
        patient_reachable=reachable,
        files_count=appointment.attachments.count(),
    )


def contact_request_alert_text(appointment) -> str:
    peer_id = appointment.vk_peer_id or appointment.vk_user_id
    return doctor_msg.contact_requested(appointment, dialog_url=vk_transport.admin_dialog_url(peer_id))

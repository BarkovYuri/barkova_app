"""
Celery-задачи уведомлений.

Все уведомления уходят из воркера, а не из HTTP-запроса пациента: медленный
VK или почта больше не тормозят запись и не роняют её по таймауту gunicorn.
Алерты врачу повторяются с нарастающей паузой; письмо на резервный email
уходит только после последней неудачной попытки в VK.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger("apps.notifications.tasks")

DOCTOR_ALERT_MAX_RETRIES = 5


def enqueue(task, *args) -> None:
    """Ставит задачу в очередь; если брокер недоступен, выполняет её на месте."""
    try:
        task.delay(*args)
    except Exception:
        logger.exception("Celery broker unavailable, running %s inline", task.name)
        try:
            task.apply(args=args)
        except Exception:
            logger.exception("Inline run of %s failed", task.name)


def _load(appointment_id: int):
    from apps.appointments.models import Appointment

    return Appointment.objects.select_related("slot").prefetch_related("attachments").filter(pk=appointment_id).first()


def _retry_doctor_alert(task, text: str, notification_type: str, appointment) -> bool:
    from django.conf import settings

    from .notifiers import alert_doctor

    if not settings.VK_DOCTOR_USER_IDS and not settings.DOCTOR_ALERT_EMAILS:
        # Получатели не настроены: повторы не помогут. Сразу фиксируем
        # неудачу в логе уведомлений, чтобы её было видно в админке.
        return alert_doctor(text, notification_type=notification_type, appointment=appointment)

    is_last_try = task.request.retries >= DOCTOR_ALERT_MAX_RETRIES
    delivered = alert_doctor(
        text,
        notification_type=notification_type,
        appointment=appointment,
        email_fallback=is_last_try,
    )
    if not delivered and not is_last_try:
        raise task.retry(countdown=30 * 2**task.request.retries)
    return delivered


# ─── VK Callback ──────────────────────────────────────────────────────────────


@shared_task
def process_vk_callback_event(event_data: dict) -> None:
    from .vk_bot import handle_event

    handle_event(event_data)


# ─── Врачу ────────────────────────────────────────────────────────────────────


@shared_task(bind=True, max_retries=DOCTOR_ALERT_MAX_RETRIES)
def alert_doctor_new_appointment(self, appointment_id: int) -> bool:
    from .notifiers import doctor_alert_sent, new_appointment_alert_text

    appointment = _load(appointment_id)
    if appointment is None or doctor_alert_sent(appointment, "created"):
        return True
    return _retry_doctor_alert(self, new_appointment_alert_text(appointment), "created", appointment)


@shared_task(bind=True, max_retries=DOCTOR_ALERT_MAX_RETRIES)
def notify_doctor_status_changed(self, appointment_id: int) -> bool:
    from .messages import doctor as doctor_msg

    appointment = _load(appointment_id)
    if appointment is None:
        return True
    return _retry_doctor_alert(
        self, doctor_msg.appointment_status_changed(appointment), appointment.status, appointment
    )


@shared_task(bind=True, max_retries=DOCTOR_ALERT_MAX_RETRIES)
def notify_doctor_contact_request(self, appointment_id: int) -> bool:
    from .notifiers import contact_request_alert_text

    appointment = _load(appointment_id)
    if appointment is None:
        return True
    return _retry_doctor_alert(self, contact_request_alert_text(appointment), "doctor_contact", appointment)


@shared_task
def send_doctor_daily_digest() -> bool:
    """Утренняя сводка: записи на сегодня и неотвеченные диалоги сообщества."""
    from apps.appointments.models import ACTIVE_STATUSES, Appointment

    from .messages import doctor as doctor_msg
    from .notifiers import alert_doctor
    from .transports import vk as vk_transport

    today = timezone.localdate()
    appointments = list(
        Appointment.objects.select_related("slot")
        .filter(slot__date=today, status__in=ACTIVE_STATUSES)
        .order_by("slot__start_time")
    )
    unanswered_ok, unanswered = vk_transport.get_unanswered_conversations()
    text = doctor_msg.daily_digest(appointments=appointments, unanswered=unanswered, unanswered_ok=unanswered_ok)
    return alert_doctor(text, notification_type="daily_digest")


# ─── Пациенту ─────────────────────────────────────────────────────────────────


@shared_task(bind=True, max_retries=3)
def deliver_booking_to_patient(self, appointment_id: int) -> str:
    """
    Сообщение пациенту о новой записи. Если сообщество пока не может ему
    писать, не повторяем: бот отправит сообщение, когда пациент напишет
    в сообщество или разрешит сообщения.
    """
    from .notifiers import send_booking_created_to_patient
    from .transports.vk import is_permanent_error

    appointment = _load(appointment_id)
    if appointment is None or not appointment.vk_user_id or appointment.patient_notified_at:
        return "skipped"

    ok, error_text = send_booking_created_to_patient(appointment)
    if ok:
        return "sent"
    if error_text == "not_allowed" or is_permanent_error(error_text):
        return "not_allowed"
    raise self.retry(countdown=60 * 2**self.request.retries)


@shared_task(bind=True, max_retries=3)
def notify_patient_status_changed(self, appointment_id: int, status: str) -> str:
    from .notifiers import send_status_to_patient
    from .transports.vk import is_permanent_error

    appointment = _load(appointment_id)
    if appointment is None or not appointment.vk_user_id:
        return "skipped"
    ok, error_text = send_status_to_patient(appointment, status)
    if ok:
        return "sent"
    if is_permanent_error(error_text):
        return "not_allowed"
    raise self.retry(countdown=60 * 2**self.request.retries)

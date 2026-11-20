import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.appointments.models import ACTIVE_STATUSES, Appointment
from apps.scheduling.timefmt import slot_start_datetime

logger = logging.getLogger("apps.appointments.tasks")

# Напоминаем примерно за 2 часа. Если запись сделана позже (закрытие записи
# за 1 час до начала), напоминание уйдёт сразу, но не раньше чем через
# REMINDER_MIN_AGE после записи, чтобы не дублировать сообщение «вы записаны».
REMINDER_LEAD = timedelta(hours=2, minutes=5)
REMINDER_LATEST = timedelta(minutes=15)
REMINDER_MIN_AGE = timedelta(minutes=20)


@shared_task
def send_appointment_reminders():
    """Напоминания пациентам в VK перед онлайн-разбором. Запускается раз в минуту."""
    from apps.notifications.services import send_reminder_to_patient
    from apps.notifications.transports.vk import is_permanent_error

    now = timezone.now()
    today = timezone.localdate()

    appointments = (
        Appointment.objects.select_related("slot")
        .filter(
            status__in=ACTIVE_STATUSES,
            reminder_sent_at__isnull=True,
            preferred_contact_method="vk",
            slot__date__in=[today, today + timedelta(days=1)],
            created_at__lte=now - REMINDER_MIN_AGE,
        )
        .exclude(vk_user_id="")
        .order_by("slot__date", "slot__start_time")
    )

    sent_ids: list[int] = []
    for appointment in appointments:
        starts_in = slot_start_datetime(appointment.slot.date, appointment.slot.start_time) - now
        if not (REMINDER_LATEST <= starts_in <= REMINDER_LEAD):
            continue

        # Atomic claim: если два воркера подхватят одну запись, отправит
        # только тот, у кого UPDATE затронул строку.
        claimed = Appointment.objects.filter(pk=appointment.pk, reminder_sent_at__isnull=True).update(
            reminder_sent_at=now
        )
        if not claimed:
            continue

        ok, error_text = send_reminder_to_patient(appointment)
        if ok:
            sent_ids.append(appointment.id)
            continue

        if is_permanent_error(error_text):
            # Пациент запретил сообщения: повторять каждую минуту бессмысленно.
            logger.warning("Reminder for appointment %s not allowed by VK: %s", appointment.id, error_text)
            continue

        logger.error("VK reminder error for appointment %s: %s", appointment.id, error_text)
        Appointment.objects.filter(pk=appointment.pk).update(reminder_sent_at=None)

    return {"sent_ids": sent_ids, "count": len(sent_ids)}

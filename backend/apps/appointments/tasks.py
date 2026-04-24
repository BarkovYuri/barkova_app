import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.notifications.services import (
    send_reminder_with_actions_telegram,
    send_reminder_with_actions_vk,
)

logger = logging.getLogger("apps.appointments.tasks")


@shared_task
def send_appointment_reminders():
    """
    Отправляет напоминания пациентам за ~2 часа до консультации.

    Оптимизация:
    - Фильтр slot__date по сегодня/завтра — не тянем всю историю.
    - logger вместо print.
    """
    now = timezone.now()
    window_start = now + timedelta(hours=1, minutes=55)
    window_end = now + timedelta(hours=2, minutes=5)
    current_tz = timezone.get_current_timezone()

    today = now.astimezone(current_tz).date()
    tomorrow = today + timedelta(days=1)

    appointments = (
        Appointment.objects.select_related("slot")
        .filter(
            status__in=["new", "confirmed"],
            reminder_sent_at__isnull=True,
            slot__date__in=[today, tomorrow],
        )
        .order_by("slot__date", "slot__start_time")
    )

    sent_ids: list[int] = []

    for appointment in appointments:
        slot_dt = timezone.make_aware(
            datetime.combine(appointment.slot.date, appointment.slot.start_time),
            current_tz,
        )

        if not (window_start <= slot_dt <= window_end):
            continue

        sent = False

        if appointment.preferred_contact_method == "telegram" and appointment.telegram_chat_id:
            ok, _, error_text = send_reminder_with_actions_telegram(appointment)
            sent = bool(ok)
            if not ok:
                logger.error(
                    "Telegram reminder error for appointment %s: %s",
                    appointment.id, error_text,
                )

        elif appointment.preferred_contact_method == "vk" and appointment.vk_user_id:
            ok, _, error_text = send_reminder_with_actions_vk(appointment)
            sent = bool(ok)
            if not ok:
                logger.error(
                    "VK reminder error for appointment %s: %s",
                    appointment.id, error_text,
                )

        if sent:
            appointment.reminder_sent_at = now
            appointment.save(update_fields=["reminder_sent_at"])
            sent_ids.append(appointment.id)
            logger.info("Reminder sent for appointment %s", appointment.id)

    return {"sent_ids": sent_ids, "count": len(sent_ids)}

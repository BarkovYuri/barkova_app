from datetime import datetime, timedelta

from celery import shared_task
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.notifications.services import (
    send_to_patient,
    send_to_patient_vk,
)


def _build_reminder_text(appointment) -> str:
    return (
        "⏰ Напоминание о консультации\n"
        f"Сегодня консультация через 2 часа.\n"
        f"Дата: {appointment.slot.date}\n"
        f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
        f"{appointment.slot.end_time.strftime('%H:%M')}\n\n"
        "Сможете присутствовать?"
    )


@shared_task
def send_appointment_reminders():
    now = timezone.now()
    window_start = now + timedelta(hours=1, minutes=55)
    window_end = now + timedelta(hours=2, minutes=5)
    current_tz = timezone.get_current_timezone()

    appointments = (
        Appointment.objects.select_related("slot")
        .filter(
            status__in=["new", "confirmed"],
            reminder_sent_at__isnull=True,
        )
        .order_by("slot__date", "slot__start_time")
    )

    sent_ids = []

    for appointment in appointments:
        slot_dt = timezone.make_aware(
            datetime.combine(appointment.slot.date, appointment.slot.start_time),
            current_tz,
        )

        if not (window_start <= slot_dt <= window_end):
            continue

        text = _build_reminder_text(appointment)

        sent = False

        if (
            appointment.preferred_contact_method == "telegram"
            and appointment.telegram_chat_id
        ):
            ok, _, _ = send_to_patient(
                appointment,
                text,
            ) or (False, "", "")
            sent = bool(ok)

        elif (
            appointment.preferred_contact_method == "vk"
            and appointment.vk_user_id
        ):
            ok, error_text = send_to_patient_vk(
                appointment,
                text,
            )
            sent = bool(ok)
            if not ok:
                print(f"VK reminder error for appointment {appointment.id}: {error_text}")

        if sent:
            appointment.reminder_sent_at = now
            appointment.save(update_fields=["reminder_sent_at"])
            sent_ids.append(appointment.id)

    return {"sent_ids": sent_ids, "count": len(sent_ids)}

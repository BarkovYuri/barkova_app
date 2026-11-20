"""
Перенос записи на другое время.

Пациент переносит запись кнопкой в VK, врач — сменой слота в админке.
Слот освобождается и занимается через sync_slot_booking, напоминание
сбрасывается, чтобы прийти уже к новому времени, а уведомление уходит той
стороне, которая перенос не делала.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.appointments.services.status import SOURCE_DOCTOR, SOURCE_PATIENT, sync_slot_booking
from apps.scheduling.models import TimeSlot
from apps.scheduling.reservation import get_reserved_slot_ids, is_slot_reserved
from apps.scheduling.services import get_available_slots_queryset
from apps.scheduling.timefmt import slot_start_datetime

logger = logging.getLogger("apps.appointments.services.reschedule")

RESCHEDULE_OPTIONS_LIMIT = 8


class RescheduleError(Exception):
    """Перенести нельзя: запись неактивна или время недоступно."""


def reschedule_options(appointment: Appointment, limit: int = RESCHEDULE_OPTIONS_LIMIT) -> list[TimeSlot]:
    """Ближайшие свободные слоты, кроме текущего и тех, что сейчас бронирует кто-то на сайте."""
    candidates = list(get_available_slots_queryset().exclude(pk=appointment.slot_id)[: limit * 2])
    reserved = get_reserved_slot_ids([slot.id for slot in candidates])
    return [slot for slot in candidates if slot.id not in reserved][:limit]


def _slot_is_bookable(slot: TimeSlot) -> bool:
    starts = slot_start_datetime(slot.date, slot.start_time)
    return slot.is_active and not slot.is_booked and starts > timezone.now() + timedelta(hours=1)


def reschedule(appointment: Appointment, new_slot_id: int, *, source: str) -> TimeSlot:
    """Переносит запись на слот new_slot_id. Бросает RescheduleError."""
    if not appointment.is_active:
        raise RescheduleError("Запись уже завершена или отменена.")
    old_slot = appointment.slot
    if int(new_slot_id) == old_slot.pk:
        return old_slot

    with transaction.atomic():
        slot = TimeSlot.objects.select_for_update().filter(pk=new_slot_id).first()
        if slot is None or not _slot_is_bookable(slot) or is_slot_reserved(slot.pk):
            raise RescheduleError("Это время уже недоступно.")

        appointment.slot = slot
        # Напоминание и ответ на него относились к старому времени.
        appointment.reminder_sent_at = None
        appointment.reminder_response = ""
        appointment.reminder_response_at = None
        try:
            with transaction.atomic():
                appointment.save(
                    update_fields=["slot", "reminder_sent_at", "reminder_response", "reminder_response_at"]
                )
        except IntegrityError as exc:
            raise RescheduleError("Это время только что заняли.") from exc

        sync_slot_booking(old_slot.pk)
        sync_slot_booking(slot.pk)
        schedule_reschedule_notifications(appointment.pk, old_slot, source)

    logger.info("Appointment %s rescheduled %s -> %s (source=%s)", appointment.pk, old_slot.pk, slot.pk, source)
    return slot


def schedule_reschedule_notifications(appointment_id: int, old_slot: TimeSlot, source: str) -> None:
    from apps.notifications import tasks
    from apps.notifications.messages.doctor import slot_text
    from apps.notifications.tasks import enqueue

    old_text = slot_text(old_slot)
    if source == SOURCE_PATIENT:
        transaction.on_commit(lambda: enqueue(tasks.notify_doctor_rescheduled, appointment_id, old_text))
    elif source == SOURCE_DOCTOR:
        transaction.on_commit(lambda: enqueue(tasks.notify_patient_rescheduled, appointment_id))

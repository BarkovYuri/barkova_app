"""
Единая точка смены статуса записи.

Раньше статус меняли в четырёх местах (бот, API админки, форма и
массовые действия в Django-админке), и только часть из них освобождала
слот и уведомляла стороны. Теперь любая смена статуса идёт через
change_status(): слот синхронизируется с реальным состоянием записей,
а уведомления уходят той стороне, которая изменение не инициировала.
"""

from __future__ import annotations

import logging

from django.db import transaction
from rest_framework import serializers

from apps.appointments.models import ACTIVE_STATUSES, Appointment
from apps.scheduling.models import TimeSlot

logger = logging.getLogger("apps.appointments.services.status")

# Статусы, при которых слот считается занятым. Завершённая запись тоже
# держит слот: это прошлое время, и оно не должно снова стать доступным.
OCCUPYING_STATUSES = (*ACTIVE_STATUSES, "completed")

SOURCE_PATIENT = "patient"
SOURCE_DOCTOR = "doctor"
SOURCE_SYSTEM = "system"


def sync_slot_booking(slot_id: int) -> None:
    """Выставляет TimeSlot.is_booked по факту наличия записей на слот."""
    occupied = Appointment.objects.filter(slot_id=slot_id, status__in=OCCUPYING_STATUSES).exists()
    slot = TimeSlot.objects.filter(pk=slot_id).first()
    if slot and slot.is_booked != occupied:
        slot.is_booked = occupied
        # save(), а не update(): сигнал TimeSlot сбрасывает кэш свободных слотов.
        slot.save(update_fields=["is_booked"])


def has_slot_conflict(appointment: Appointment, slot_id: int, status: str) -> bool:
    """Займёт ли запись в этом статусе слот, на котором уже есть другая активная запись."""
    if status not in ACTIVE_STATUSES:
        return False
    qs = Appointment.objects.filter(slot_id=slot_id, status__in=ACTIVE_STATUSES)
    if appointment.pk:
        qs = qs.exclude(pk=appointment.pk)
    return qs.exists()


def schedule_status_notifications(appointment_id: int, new_status: str, source: str) -> None:
    """Уведомляет сторону, которая изменение не инициировала."""
    from apps.notifications import tasks
    from apps.notifications.tasks import enqueue

    if new_status not in {"confirmed", "cancelled"}:
        return
    if source == SOURCE_PATIENT:
        transaction.on_commit(lambda: enqueue(tasks.notify_doctor_status_changed, appointment_id))
    elif source == SOURCE_DOCTOR:
        transaction.on_commit(lambda: enqueue(tasks.notify_patient_status_changed, appointment_id, new_status))


def change_status(appointment: Appointment, new_status: str, *, source: str) -> bool:
    """
    Меняет статус записи. Возвращает True, если статус изменился.

    Бросает ValidationError, если запись нельзя вернуть в активный статус,
    потому что её слот уже занят другой записью.
    """
    old_status = appointment.status
    if old_status == new_status:
        return False

    if has_slot_conflict(appointment, appointment.slot_id, new_status):
        raise serializers.ValidationError(
            {"status": "На это время уже есть другая активная запись. Сначала перенесите или отмените её."}
        )

    with transaction.atomic():
        appointment.status = new_status
        appointment.save(update_fields=["status"])
        sync_slot_booking(appointment.slot_id)
        schedule_status_notifications(appointment.pk, new_status, source)

    logger.info("Appointment %s status %s -> %s (source=%s)", appointment.pk, old_status, new_status, source)
    return True

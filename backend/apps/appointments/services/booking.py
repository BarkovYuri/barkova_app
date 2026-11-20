"""
BookingService — бизнес-логика создания записи.

Перенесено из appointments/serializers.py, где функции
_create_appointment_with_slot_lock / _get_available_slot_or_error
жили рядом с сериализационным кодом.
"""
from __future__ import annotations

import logging
import secrets
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from apps.appointments.models import Appointment, AppointmentAttachment
from apps.content.models import LegalDocument
from apps.scheduling.models import TimeSlot
from apps.scheduling.timefmt import slot_start_datetime

logger = logging.getLogger("apps.appointments.services.booking")

def get_available_slot_or_error(slot_id: int) -> TimeSlot:
    """
    Возвращает активный и свободный слот, доступный для записи.
    Бросает ValidationError если слот недоступен или слишком близко по времени.
    """
    try:
        slot = TimeSlot.objects.get(id=slot_id, is_active=True)
    except TimeSlot.DoesNotExist:
        raise serializers.ValidationError({"slot_id": "Слот не найден или недоступен."}) from None

    if slot.is_booked:
        raise serializers.ValidationError({"slot_id": "Этот слот уже занят."})

    if slot_start_datetime(slot.date, slot.start_time) <= timezone.now() + timedelta(hours=1):
        raise serializers.ValidationError(
            {"slot_id": "Запись на это время уже закрыта. Выберите слот позже чем через 1 час."}
        )

    return slot


def get_active_legal_versions() -> dict:
    """Возвращает версии активных юридических документов для сохранения в записи."""

    def _latest(doc_type: str) -> str:
        doc = (
            LegalDocument.objects
            .filter(doc_type=doc_type, is_active=True)
            .order_by("-created_at")
            .first()
        )
        return doc.version if doc else ""

    return {
        "legal_offer_version":    _latest("offer"),
        "legal_privacy_version":  _latest("privacy"),
        "legal_consent_version":  _latest("consent"),
    }


def create_appointment_with_slot_lock(
    *,
    slot: TimeSlot,
    appointment_data: dict,
    files: list | None = None,
) -> Appointment:
    """
    Атомарно создаёт запись с блокировкой слота (select_for_update).
    После коммита запускает уведомления через transaction.on_commit.
    """
    files = files or []

    locked_slot = TimeSlot.objects.select_for_update().get(id=slot.id)

    if not locked_slot.is_active:
        raise serializers.ValidationError({"slot_id": "Этот слот недоступен для записи."})

    if locked_slot.is_booked:
        raise serializers.ValidationError({"slot_id": "Этот слот уже занят."})

    legal_versions = get_active_legal_versions()

    try:
        appointment = Appointment.objects.create(
            slot=locked_slot,
            vk_link_token=secrets.token_urlsafe(16),
            **appointment_data,
            **legal_versions,
        )
    except IntegrityError as exc:
        raise serializers.ValidationError(
            {"slot_id": "Этот слот уже только что заняли. Пожалуйста, выберите другое время."}
        ) from exc

    for file in files:
        AppointmentAttachment.objects.create(appointment=appointment, file=file)

    locked_slot.is_booked = True
    locked_slot.save(update_fields=["is_booked"])

    def _notify() -> None:
        # Уведомления — в Celery: медленный VK не должен тормозить ответ
        # пациенту и не может уронить запись по таймауту gunicorn.
        from apps.notifications import tasks
        from apps.notifications.tasks import enqueue

        enqueue(tasks.alert_doctor_new_appointment, appointment.pk)
        if appointment.preferred_contact_method == "vk" and appointment.vk_user_id:
            enqueue(tasks.deliver_booking_to_patient, appointment.pk)

    transaction.on_commit(_notify)
    logger.info("Appointment %s created for slot %s", appointment.id, locked_slot.id)
    return appointment

"""
BookingService — бизнес-логика создания записи.

Перенесено из appointments/serializers.py, где функции
_create_appointment_with_slot_lock / _get_available_slot_or_error
жили рядом с сериализационным кодом.
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from apps.content.models import LegalDocument
from apps.scheduling.models import TimeSlot
from apps.appointments.models import Appointment, AppointmentAttachment

logger = logging.getLogger("apps.appointments.services.booking")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx", ".heic"}


def get_available_slot_or_error(slot_id: int) -> TimeSlot:
    """
    Возвращает активный и свободный слот, доступный для записи.
    Бросает ValidationError если слот недоступен или слишком близко по времени.
    """
    try:
        slot = TimeSlot.objects.get(id=slot_id, is_active=True)
    except TimeSlot.DoesNotExist:
        raise serializers.ValidationError({"slot_id": "Слот не найден или недоступен."})

    if slot.is_booked:
        raise serializers.ValidationError({"slot_id": "Этот слот уже занят."})

    current_tz = timezone.get_current_timezone()
    slot_dt = timezone.make_aware(
        datetime.combine(slot.date, slot.start_time),
        current_tz,
    )
    threshold = timezone.now() + timedelta(hours=1)

    if slot_dt <= threshold:
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
            telegram_link_token=secrets.token_urlsafe(16),
            vk_link_token=secrets.token_urlsafe(16),
            **appointment_data,
            **legal_versions,
        )
    except IntegrityError:
        raise serializers.ValidationError(
            {"slot_id": "Этот слот уже только что заняли. Пожалуйста, выберите другое время."}
        )

    for file in files:
        AppointmentAttachment.objects.create(appointment=appointment, file=file)

    locked_slot.is_booked = True
    locked_slot.save(update_fields=["is_booked"])

    def _notify() -> None:
        from apps.notifications.services import (
            send_appointment_created_notification,
            send_created_message_to_patient_with_actions,
            send_created_message_to_patient_with_actions_vk,
        )
        appt = (
            Appointment.objects
            .select_related("slot")
            .prefetch_related("attachments")
            .get(pk=appointment.pk)
        )
        send_appointment_created_notification(appt)

        if appt.preferred_contact_method == "telegram" and appt.telegram_chat_id:
            send_created_message_to_patient_with_actions(appt)

        if appt.preferred_contact_method == "vk" and appt.vk_user_id:
            send_created_message_to_patient_with_actions_vk(appt)

    transaction.on_commit(_notify)
    logger.info("Appointment %s created for slot %s", appointment.id, locked_slot.id)
    return appointment

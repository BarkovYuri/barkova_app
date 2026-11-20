"""
Действия пациента над записью из VK: подтвердить, отменить, ответить на
напоминание, попросить связь с врачом.

Статус меняется только через services.status.change_status(), поэтому слот
освобождается, а врач получает алерт в любом сценарии.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from django.utils import timezone

from apps.appointments.services.status import SOURCE_PATIENT, change_status
from apps.notifications.keyboards import vk as vk_kb
from apps.notifications.messages import patient as patient_msg

logger = logging.getLogger("apps.appointments.services.actions")

# Из каких статусов допустимо каждое действие. Старые кнопки в истории
# переписки не должны менять завершённую или отменённую запись.
_ALLOWED_TRANSITIONS = {
    "confirm": {"new"},
    "cancel": {"new", "confirmed"},
    "yes": {"new", "confirmed"},
    "no": {"new", "confirmed"},
    "doctor": {"new", "confirmed"},
}


def is_action_allowed(action: str, current_status: str) -> bool:
    return current_status in _ALLOWED_TRANSITIONS.get(action, set())


class AppointmentActionService:
    @staticmethod
    def handle(appointment, action: str) -> dict:
        from apps.notifications.notifiers import send_to_patient_vk

        return handle_action(appointment, action, send_fn=send_to_patient_vk)


def handle_action(appointment, action: str, send_fn: Callable) -> dict:
    """
    Выполняет действие и отвечает пациенту через send_fn(appointment, text, keyboard=None).
    Возвращает {"status": ..., "changed": bool} или {"error": "unknown_action"}.
    """
    if action not in _ALLOWED_TRANSITIONS:
        logger.warning("Unknown action '%s' for appointment %s", action, appointment.id)
        return {"error": "unknown_action"}

    if not is_action_allowed(action, appointment.status):
        send_fn(appointment, patient_msg.action_not_allowed())
        return {"status": "not_allowed", "changed": False}

    if action == "confirm":
        changed = change_status(appointment, "confirmed", source=SOURCE_PATIENT)
        if changed:
            send_fn(appointment, patient_msg.confirmed_by_patient(appointment), keyboard=vk_kb.active_root(appointment))
        return {"status": "confirmed", "changed": changed}

    if action == "cancel":
        changed = change_status(appointment, "cancelled", source=SOURCE_PATIENT)
        if changed:
            send_fn(appointment, patient_msg.cancelled_by_patient(appointment), keyboard=vk_kb.booking())
        return {"status": "cancelled", "changed": changed}

    if action == "yes":
        changed = appointment.reminder_response != "yes"
        if changed:
            appointment.reminder_response = "yes"
            appointment.reminder_response_at = timezone.now()
            appointment.save(update_fields=["reminder_response", "reminder_response_at"])
            send_fn(appointment, patient_msg.reminder_yes(appointment), keyboard=vk_kb.active_root(appointment))
        return {"status": "reminder_yes", "changed": changed}

    if action == "no":
        appointment.reminder_response = "no"
        appointment.reminder_response_at = timezone.now()
        appointment.save(update_fields=["reminder_response", "reminder_response_at"])
        changed = change_status(appointment, "cancelled", source=SOURCE_PATIENT)
        send_fn(appointment, patient_msg.reminder_no(appointment), keyboard=vk_kb.booking())
        return {"status": "reminder_no", "changed": changed}

    # action == "doctor"
    from apps.notifications import tasks
    from apps.notifications.tasks import enqueue
    from apps.notifications.transports import vk as vk_transport

    changed = appointment.reminder_response != "doctor_contact"
    if changed:
        now = timezone.now()
        appointment.reminder_response = "doctor_contact"
        appointment.reminder_response_at = now
        appointment.doctor_contact_requested_at = now
        appointment.save(update_fields=["reminder_response", "reminder_response_at", "doctor_contact_requested_at"])
        enqueue(tasks.notify_doctor_contact_request, appointment.pk)
        send_fn(appointment, patient_msg.doctor_will_contact(appointment), keyboard=vk_kb.active_root(appointment))
        # Ответ бота перевёл диалог в «отвеченные». Возвращаем его в
        # неотвеченные, чтобы врач увидел просьбу в интерфейсе сообщества.
        vk_transport.mark_unanswered(appointment.vk_peer_id or appointment.vk_user_id)
    return {"status": "doctor_contact_requested", "changed": changed}

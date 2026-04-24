"""
AppointmentActionService — единый обработчик действий пациента над записью.

Заменяет дублирующиеся switch-блоки в TelegramAppointmentActionView
и VKAppointmentActionView. Транспорт передаётся через callable:
  send_fn(appointment, text, keyboard=None)
"""
from __future__ import annotations

import logging
from typing import Callable

from django.utils import timezone

from apps.notifications.services import (
    send_appointment_status_notification,
    send_doctor_contact_request_notification,
    build_vk_active_root_keyboard,
    build_vk_booking_keyboard,
)

logger = logging.getLogger("apps.appointments.services.actions")


class AppointmentActionService:
    """Фасад для удобного использования из views."""

    @staticmethod
    def handle(appointment, action: str, channel: str) -> dict:
        from apps.notifications.services import send_to_patient, send_to_patient_vk
        send_fn = send_to_patient if channel == "telegram" else send_to_patient_vk
        return handle_action(appointment, action, send_fn=send_fn)


def _slot_time_str(appointment) -> str:
    slot = appointment.slot
    return (
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}"
    )


def handle_action(
    appointment,
    action: str,
    send_fn: Callable,
) -> dict:
    """
    Выполняет действие над записью и отправляет ответ пациенту через send_fn.

    send_fn(appointment, text, keyboard=None) — транспортная функция
      (send_to_patient для Telegram, send_to_patient_vk для VK).

    Возвращает dict с полями status и (опционально) changed,
    либо {"error": "unknown_action"} для неизвестного действия.
    """
    if action == "confirm":
        changed = appointment.status != "confirmed"
        if changed:
            appointment.status = "confirmed"
            appointment.save(update_fields=["status"])
            send_appointment_status_notification(appointment)
            send_fn(
                appointment,
                "✅ Запись подтверждена\n" + _slot_time_str(appointment),
                keyboard=build_vk_active_root_keyboard(appointment),
            )
        return {"status": "confirmed", "changed": changed}

    if action == "cancel":
        changed = appointment.status != "cancelled"
        if changed:
            appointment.status = "cancelled"
            appointment.save(update_fields=["status"])

            slot = appointment.slot
            if slot.is_booked:
                slot.is_booked = False
                slot.save(update_fields=["is_booked"])

            send_appointment_status_notification(appointment)
            send_fn(
                appointment,
                "❌ Запись отменена\n" + _slot_time_str(appointment),
                keyboard=build_vk_booking_keyboard(),
            )
        return {"status": "cancelled", "changed": changed}

    if action == "yes":
        changed = appointment.reminder_response != "yes"
        if changed:
            appointment.reminder_response = "yes"
            appointment.reminder_response_at = timezone.now()
            appointment.save(update_fields=["reminder_response", "reminder_response_at"])
            send_fn(
                appointment,
                "✅ Отлично, ждём вас на консультации.\n" + _slot_time_str(appointment),
                keyboard=build_vk_active_root_keyboard(appointment),
            )
        return {"status": "reminder_yes", "changed": changed}

    if action == "no":
        changed = appointment.status != "cancelled" or appointment.reminder_response != "no"
        appointment.reminder_response = "no"
        appointment.reminder_response_at = timezone.now()
        if appointment.status != "cancelled":
            appointment.status = "cancelled"
        appointment.save(update_fields=["reminder_response", "reminder_response_at", "status"])

        if changed:
            slot = appointment.slot
            if slot.is_booked:
                slot.is_booked = False
                slot.save(update_fields=["is_booked"])
            send_appointment_status_notification(appointment)

        send_fn(
            appointment,
            "❌ Запись отменена по вашему ответу на напоминание.\n" + _slot_time_str(appointment),
            keyboard=build_vk_booking_keyboard(),
        )
        return {"status": "reminder_no", "changed": changed}

    if action == "doctor":
        changed = appointment.reminder_response != "doctor_contact"
        if changed:
            now = timezone.now()
            appointment.reminder_response = "doctor_contact"
            appointment.reminder_response_at = now
            appointment.doctor_contact_requested_at = now
            appointment.save(update_fields=[
                "reminder_response",
                "reminder_response_at",
                "doctor_contact_requested_at",
            ])
            send_doctor_contact_request_notification(appointment)
            send_fn(
                appointment,
                "💬 Передали врачу, что вам нужна связь. С вами свяжутся.",
                keyboard=build_vk_active_root_keyboard(appointment),
            )
        return {"status": "doctor_contact_requested", "changed": changed}

    logger.warning("Unknown action '%s' for appointment %s", action, appointment.id)
    return {"error": "unknown_action"}

"""Публичный фасад уведомлений для остальных приложений."""

from .notifiers import (  # noqa: F401
    alert_doctor,
    send_booking_created_to_patient,
    send_reminder_to_patient,
    send_status_to_patient,
    send_to_patient_vk,
)

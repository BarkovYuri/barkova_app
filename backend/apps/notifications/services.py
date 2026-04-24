"""
notifications/services.py — backward-compatible фасад.

Весь код перемещён в:
  notifiers.py             — высокоуровневая логика
  transports/telegram.py   — Telegram HTTP-транспорт
  transports/vk.py         — VK HTTP-транспорт
  keyboards/telegram.py    — Telegram клавиатуры
  keyboards/vk.py          — VK клавиатуры
  messages/doctor.py       — форматтеры врача
  messages/patient.py      — форматтеры пациента

Этот файл реэкспортирует все публичные имена для обратной совместимости
со старыми импортами в views.py, serializers.py, tasks.py, vk_bot.py.
"""

from .notifiers import (  # noqa: F401
    send_to_patient,
    send_to_patient_vk,
    send_appointment_created_notification,
    send_appointment_status_notification,
    send_doctor_contact_request_notification,
    send_created_message_to_patient_with_actions,
    send_created_message_to_patient_with_actions_vk,
    send_reminder_with_actions_telegram,
    send_reminder_with_actions_vk,
    get_vk_remove_keyboard,
    build_vk_new_appointment_keyboard,
    build_vk_reminder_keyboard,
    build_vk_booking_keyboard,
    build_vk_active_root_keyboard,
    build_vk_manage_keyboard,
    _vk_is_messages_allowed,
)

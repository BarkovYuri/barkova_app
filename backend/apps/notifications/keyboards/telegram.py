"""Telegram inline-клавиатуры для записей пациентов."""
from __future__ import annotations


def new_appointment(appointment) -> dict:
    """Кнопки «Подтвердить» / «Отменить» для новой записи."""
    appt_id = appointment.id
    token = appointment.telegram_link_token
    return {
        "inline_keyboard": [
            [
                {"text": "Подтвердить", "callback_data": f"confirm:{appt_id}:{token}"},
                {"text": "Отменить",    "callback_data": f"cancel:{appt_id}:{token}"},
            ]
        ]
    }


def reminder(appointment) -> dict:
    """Кнопки «Смогу» / «Не смогу» / «Связь с врачом» для напоминания."""
    appt_id = appointment.id
    token = appointment.telegram_link_token
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Смогу",         "callback_data": f"yes:{appt_id}:{token}"},
                {"text": "❌ Не смогу",      "callback_data": f"no:{appt_id}:{token}"},
            ],
            [
                {"text": "💬 Связь с врачом", "callback_data": f"doctor:{appt_id}:{token}"},
            ],
        ]
    }

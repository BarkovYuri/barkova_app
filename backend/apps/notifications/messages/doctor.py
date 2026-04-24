"""Форматтеры уведомлений врача."""
from __future__ import annotations


def appointment_created(appointment) -> str:
    slot = appointment.slot
    reason = appointment.reason.strip() if appointment.reason else "Не указана"
    contact = appointment.preferred_contact_method or "не указан"
    return (
        "<b>Новая запись</b>\n"
        f"Пациент: {appointment.name}\n"
        f"Телефон: {appointment.phone}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Причина: {reason}\n"
        f"Способ связи: {contact}\n"
        f"Telegram: {appointment.telegram_username or '—'}\n"
        f"Статус: {appointment.get_status_display()}"
    )


def appointment_status_changed(appointment) -> str:
    slot = appointment.slot
    return (
        "<b>Изменение статуса записи</b>\n"
        f"Пациент: {appointment.name}\n"
        f"Телефон: {appointment.phone}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Новый статус: {appointment.get_status_display()}"
    )


def contact_requested(appointment) -> str:
    slot = appointment.slot
    return (
        "<b>Пациент просит связаться</b>\n"
        f"Пациент: {appointment.name}\n"
        f"Телефон: {appointment.phone}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Способ связи: {appointment.preferred_contact_method or 'не указан'}"
    )

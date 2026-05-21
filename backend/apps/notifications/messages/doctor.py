"""Форматтеры уведомлений врача.

ВАЖНО: Telegram-сообщения отправляются с parse_mode=HTML, поэтому
любые юзерские поля (name/phone/reason/telegram_username) экранируем
через html.escape() — иначе пациент с именем «<a href=evil>Иван</a>»
оформит фишинговую ссылку в сообщении врачу (баг #13 из аудита).
"""
from __future__ import annotations

from html import escape as _esc


def _safe(value) -> str:
    if value is None:
        return ""
    return _esc(str(value), quote=False)


def appointment_created(appointment) -> str:
    slot = appointment.slot
    reason = appointment.reason.strip() if appointment.reason else "Не указана"
    contact = appointment.preferred_contact_method or "не указан"
    return (
        "<b>Новая запись</b>\n"
        f"Пациент: {_safe(appointment.name)}\n"
        f"Телефон: {_safe(appointment.phone)}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Причина: {_safe(reason)}\n"
        f"Способ связи: {_safe(contact)}\n"
        f"Telegram: {_safe(appointment.telegram_username) or '—'}\n"
        f"Статус: {_safe(appointment.get_status_display())}"
    )


def appointment_status_changed(appointment) -> str:
    slot = appointment.slot
    return (
        "<b>Изменение статуса записи</b>\n"
        f"Пациент: {_safe(appointment.name)}\n"
        f"Телефон: {_safe(appointment.phone)}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Новый статус: {_safe(appointment.get_status_display())}"
    )


def contact_requested(appointment) -> str:
    slot = appointment.slot
    return (
        "<b>Пациент просит связаться</b>\n"
        f"Пациент: {_safe(appointment.name)}\n"
        f"Телефон: {_safe(appointment.phone)}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}\n"
        f"Способ связи: {_safe(appointment.preferred_contact_method) or 'не указан'}"
    )

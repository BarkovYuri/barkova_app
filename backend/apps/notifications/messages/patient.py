"""Форматтеры уведомлений пациента."""
from __future__ import annotations


def _slot_line(appointment) -> str:
    slot = appointment.slot
    return (
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}"
    )


def booking_created(appointment) -> str:
    return (
        "✅ Вы записаны на онлайн-консультацию\n"
        f"{_slot_line(appointment)}\n\n"
        "Пожалуйста, подтвердите запись кнопкой ниже.\n"
        "Если планы изменятся, вы сможете отменить запись кнопкой ниже "
        "или просто написать сообщение в этот чат."
    )


def booking_created_vk(appointment) -> str:
    return (
        "✅ Вы записаны на онлайн-консультацию\n"
        f"{_slot_line(appointment)}\n\n"
        "Пожалуйста, подтвердите запись кнопкой ниже."
    )


def reminder(appointment) -> str:
    return (
        "⏰ Напоминание о консультации\n"
        f"Сегодня консультация через 2 часа\n\n"
        f"{_slot_line(appointment)}\n\n"
        "Сможете присутствовать?"
    )

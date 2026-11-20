"""
Тексты сообщений пациенту в VK. Единственный источник правды для всех
фраз бота и уведомлений.

VK не поддерживает разметку, поэтому только plain-text и эмодзи.
"""

from __future__ import annotations

from datetime import date as date_type

from apps.scheduling.timefmt import timezone_label

WEEKDAY_RU = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "воскресенье",
}

MONTH_RU = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}

DIVIDER = "━━━━━━━━━━━━━━━"

INFORMATIONAL_NOTE = (
    "Онлайн-разбор носит информационный характер, не является медицинской услугой и не заменяет очный приём врача."
)


def format_date_human(d: date_type) -> str:
    """29 апреля, среда"""
    return f"{d.day} {MONTH_RU[d.month]}, {WEEKDAY_RU[d.weekday()]}"


def slot_card(appointment) -> str:
    slot = appointment.slot
    return f"📅 {format_date_human(slot.date)}\n🕐 {slot.start_time:%H:%M}–{slot.end_time:%H:%M} {timezone_label()}"


# ─── Уведомления о записи ─────────────────────────────────────────────────────


def booking_created(appointment) -> str:
    return (
        "✅ Вы записаны на онлайн-разбор\n\n"
        f"{slot_card(appointment)}\n\n"
        f"{DIVIDER}\n"
        "Пожалуйста, подтвердите запись кнопкой ниже. "
        "Если планы изменятся, запись можно отменить здесь же.\n\n"
        f"{INFORMATIONAL_NOTE}"
    )


def reminder(appointment) -> str:
    return (
        "⏰ Напоминание об онлайн-разборе\n\n"
        f"{slot_card(appointment)}\n\n"
        f"{DIVIDER}\n"
        "Сможете присутствовать? Ответьте кнопкой ниже."
    )


def confirmed_by_doctor(appointment) -> str:
    return f"✅ Врач подтвердил вашу запись\n\n{slot_card(appointment)}\n\n{DIVIDER}\nДетали врач уточнит в этом чате."


def cancelled_by_doctor(appointment) -> str:
    return (
        "❌ Запись отменена врачом\n\n"
        f"{slot_card(appointment)}\n\n"
        f"{DIVIDER}\n"
        "Приносим извинения. Выбрать другое время можно на сайте, "
        "а если есть вопросы, напишите сюда."
    )


def confirmed_by_patient(appointment) -> str:
    return f"✅ Запись подтверждена\n\n{slot_card(appointment)}"


def cancelled_by_patient(appointment) -> str:
    return f"❌ Запись отменена\n\n{slot_card(appointment)}\n\nЗаписаться на другое время можно по кнопке ниже."


def reminder_yes(appointment) -> str:
    return f"✅ Отлично, ждём вас на онлайн-разборе.\n\n{slot_card(appointment)}"


def reminder_no(appointment) -> str:
    return (
        f"❌ Запись отменена по вашему ответу на напоминание.\n\n{slot_card(appointment)}\n\n"
        "Записаться на другое время можно по кнопке ниже."
    )


def doctor_will_contact(appointment) -> str:
    return (
        "💬 Передали врачу, что вам нужна связь.\n\n"
        f"{slot_card(appointment)}\n\n"
        "Врач ответит в этом чате. Если вопрос срочный, позвоните по телефону с сайта."
    )


def action_not_allowed() -> str:
    return "Эта запись уже завершена или отменена, изменить её нельзя. Новую запись можно оформить на сайте."


# ─── Диалог с ботом ───────────────────────────────────────────────────────────


def greeting() -> str:
    return (
        "Здравствуйте! Это сообщество врача-инфекциониста.\n\n"
        "Записаться на онлайн-разбор можно по кнопке ниже. "
        "Если у вас вопрос, просто напишите его здесь: врач прочитает и ответит лично."
    )


def manage_prompt(appointment) -> str:
    return f"Что вы хотите сделать с записью?\n\n{slot_card(appointment)}"


def cancel_confirm_prompt(appointment) -> str:
    return f"Вы действительно хотите отменить запись?\n\n{slot_card(appointment)}"


def kept(appointment) -> str:
    return f"✅ Запись оставлена без изменений.\n\n{slot_card(appointment)}"


# ─── Перенос записи ───────────────────────────────────────────────────────────


def reschedule_prompt(appointment) -> str:
    return (
        "Выберите новое время кнопкой ниже.\n\n"
        f"Сейчас вы записаны:\n{slot_card(appointment)}\n\n"
        f"Время указано {timezone_label()}."
    )


def reschedule_no_slots() -> str:
    return (
        "Свободного времени для переноса сейчас нет. "
        "Напишите сюда, какое время вам удобно: врач подберёт вариант и ответит лично."
    )


def reschedule_unavailable() -> str:
    return "Это время только что заняли или оно уже недоступно. Выберите другое, пожалуйста."


def rescheduled(appointment) -> str:
    return f"✅ Запись перенесена\n\n{slot_card(appointment)}"


def rescheduled_by_doctor(appointment) -> str:
    return (
        "🔁 Время вашей записи изменено врачом\n\n"
        f"{slot_card(appointment)}\n\n"
        f"{DIVIDER}\n"
        "Если новое время неудобно, нажмите «Управление записью» или напишите сюда."
    )


# ─── Быстрые ответы и нерабочее время ─────────────────────────────────────────


def faq_answer(question: str, answer: str) -> str:
    return f"❓ {question}\n\n{answer}\n\nЕсли остались вопросы, напишите их сюда: врач ответит лично."


def off_hours_note(work_start: str) -> str:
    return (
        "Сейчас нерабочее время. Врач прочитает ваше сообщение и ответит "
        f"после {work_start} {timezone_label()}."
    )

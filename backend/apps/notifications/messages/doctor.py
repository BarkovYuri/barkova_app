"""Тексты алертов врачу. Канал — личные сообщения VK от сообщества, резерв — email.

Пишем plain-text: VK не поддерживает разметку, а в email HTML не нужен.
"""

from __future__ import annotations

from django.conf import settings

from apps.notifications.messages.patient import format_date_human
from apps.scheduling.timefmt import timezone_label

_REASON_LIMIT = 500
_INCOMING_LIMIT = 600


def _clip(text: str, limit: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _slot_line(appointment) -> str:
    slot = appointment.slot
    return f"{format_date_human(slot.date)}, {slot.start_time:%H:%M}–{slot.end_time:%H:%M} ({timezone_label()})"


def admin_url(appointment) -> str:
    return f"{settings.PUBLIC_BASE_URL}/admin/appointments/appointment/{appointment.pk}/change/"


def _vk_profile_line(appointment) -> str:
    if not appointment.vk_user_id:
        return "VK пациента: не привязан"
    return f"VK пациента: https://vk.com/id{appointment.vk_user_id}"


def appointment_created(appointment, *, patient_reachable: bool | None, files_count: int) -> str:
    reason = _clip(appointment.reason, _REASON_LIMIT) or "не указана"
    lines = [
        "🆕 Новая запись на онлайн-разбор",
        "",
        f"Пациент: {appointment.name}",
        f"Телефон: {appointment.phone}",
        f"Когда: {_slot_line(appointment)}",
        f"Причина: {reason}",
    ]
    if files_count:
        lines.append(f"Файлов приложено: {files_count} (смотреть в карточке записи)")
    lines.append(_vk_profile_line(appointment))
    if patient_reachable is False:
        lines += [
            "",
            "⚠️ Пациент не разрешил сообщения от сообщества, подтверждение ему не ушло. "
            "Оно придёт автоматически, как только он напишет в сообщество. "
            "Если запись скоро, лучше позвонить.",
        ]
    lines += ["", f"Карточка записи: {admin_url(appointment)}"]
    return "\n".join(lines)


_STATUS_TITLES = {
    "confirmed": "✅ Пациент подтвердил запись",
    "cancelled": "❌ Пациент отменил запись",
}


def appointment_status_changed(appointment) -> str:
    title = _STATUS_TITLES.get(appointment.status, f"Статус записи: {appointment.get_status_display()}")
    return "\n".join(
        [
            title,
            "",
            f"Пациент: {appointment.name}",
            f"Телефон: {appointment.phone}",
            f"Когда: {_slot_line(appointment)}",
            "",
            f"Карточка записи: {admin_url(appointment)}",
        ]
    )


def contact_requested(appointment, *, dialog_url: str) -> str:
    return "\n".join(
        [
            "💬 Пациент просит связаться",
            "",
            f"Пациент: {appointment.name}",
            f"Телефон: {appointment.phone}",
            f"Запись: {_slot_line(appointment)}",
            "",
            f"Открыть диалог: {dialog_url}",
            f"Карточка записи: {admin_url(appointment)}",
        ]
    )


def incoming_message(
    *,
    sender_name: str,
    user_id: str,
    text: str,
    attachments_summary: str,
    appointment,
    dialog_url: str,
) -> str:
    who = sender_name or f"id{user_id}"
    lines = [f"✉️ Новое сообщение в сообществе от {who}", ""]
    body = _clip(text, _INCOMING_LIMIT)
    if body:
        lines.append(f"«{body}»")
    if attachments_summary:
        lines.append(f"Вложения: {attachments_summary}")
    if appointment is not None:
        lines += ["", f"У пациента есть запись: {_slot_line(appointment)}"]
    lines += [
        "",
        f"Ответить: {dialog_url}",
        "Следующие сообщения этого человека в ближайшие "
        f"{settings.VK_DOCTOR_ALERT_COOLDOWN_MINUTES} мин. отдельно не дублируются.",
    ]
    return "\n".join(lines)


def daily_digest(*, appointments: list, unanswered: list[dict] | None, unanswered_ok: bool) -> str:
    lines = ["☀️ Сводка на сегодня", ""]
    if appointments:
        lines.append(f"Онлайн-разборы ({len(appointments)}):")
        for appt in appointments:
            slot = appt.slot
            mark = "✅" if appt.status == "confirmed" else "🕐"
            reach = "" if appt.patient_notified_at else " ⚠️ не получил сообщение в VK"
            lines.append(f"{mark} {slot.start_time:%H:%M} {appt.name}, {appt.phone}{reach}")
    else:
        lines.append("Онлайн-разборов на сегодня нет.")

    lines.append("")
    if not unanswered_ok:
        lines.append("Не удалось получить список неотвеченных диалогов, проверьте сообщения сообщества вручную.")
    elif unanswered:
        lines.append(f"Неотвеченные диалоги в сообществе: {len(unanswered)}")
        for item in unanswered[:10]:
            peer_id = item.get("conversation", {}).get("peer", {}).get("id")
            if peer_id:
                lines.append(f"• https://vk.com/gim{settings.VK_GROUP_ID}?sel={peer_id}")
        if len(unanswered) > 10:
            lines.append("…и ещё несколько, откройте раздел «Неотвеченные».")
    else:
        lines.append("Неотвеченных диалогов нет.")
    return "\n".join(lines)


def test_alert() -> str:
    return (
        "🔔 Проверка оповещений сайта.\n\n"
        "Если вы видите это сообщение, алерты о записях и входящих сообщениях будут приходить сюда."
    )


def appointment_rescheduled(appointment, old_slot_text: str) -> str:
    return "\n".join(
        [
            "🔁 Пациент перенёс запись",
            "",
            f"Пациент: {appointment.name}",
            f"Телефон: {appointment.phone}",
            f"Было: {old_slot_text}",
            f"Стало: {_slot_line(appointment)}",
            "",
            f"Карточка записи: {admin_url(appointment)}",
        ]
    )


def reschedule_without_slots(appointment, *, dialog_url: str) -> str:
    return "\n".join(
        [
            "🔁 Пациент хочет перенести запись, но свободных слотов нет",
            "",
            f"Пациент: {appointment.name}",
            f"Телефон: {appointment.phone}",
            f"Текущая запись: {_slot_line(appointment)}",
            "",
            f"Ответить: {dialog_url}",
        ]
    )


def slot_text(slot) -> str:
    """Текст слота для истории «было/стало»."""
    from apps.notifications.messages.patient import format_date_human

    return f"{format_date_human(slot.date)}, {slot.start_time:%H:%M}–{slot.end_time:%H:%M}"

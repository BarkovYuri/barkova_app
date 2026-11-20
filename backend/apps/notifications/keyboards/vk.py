"""
VK-клавиатуры для записей пациентов. Единственный источник правды:
ими пользуются и уведомления, и бот.
"""
from __future__ import annotations

import json

from django.conf import settings

from apps.notifications.vk_constants import (
    VK_CMD_CANCEL_CONFIRM,
    VK_CMD_CANCEL_KEEP,
    VK_CMD_CANCEL_REQUEST,
    VK_CMD_CONFIRM,
    VK_CMD_DOCTOR,
    VK_CMD_FAQ,
    VK_CMD_MANAGE,
    VK_CMD_RESCHEDULE_REQUEST,
    VK_CMD_RESCHEDULE_TO,
    VK_CMD_YES,
)


def _btn(label: str, cmd: str, appointment, color: str, **extra) -> dict:
    return {
        "action": {
            "type": "callback",
            "label": label[:40],
            "payload": json.dumps(
                {"cmd": cmd, "appointment_id": appointment.id, "token": appointment.vk_link_token, **extra},
                ensure_ascii=False,
            ),
        },
        "color": color,
    }


def new_appointment(appointment) -> dict:
    """Кнопки «Подтвердить» / «Отменить» для новой записи."""
    return {
        "one_time": False,
        "inline": False,
        "buttons": [[
            _btn("Подтвердить", VK_CMD_CONFIRM,          appointment, "positive"),
            _btn("Отменить",    VK_CMD_CANCEL_REQUEST,    appointment, "negative"),
        ]],
    }


def reminder(appointment) -> dict:
    """Кнопки «Смогу» / «Не смогу» / «Перенести» / «Связь с врачом» для напоминания."""
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                _btn("Смогу",          VK_CMD_YES,           appointment, "positive"),
                _btn("Не смогу",       VK_CMD_CANCEL_REQUEST, appointment, "negative"),
            ],
            [
                _btn("Перенести",      VK_CMD_RESCHEDULE_REQUEST, appointment, "secondary"),
                _btn("Связь с врачом", VK_CMD_DOCTOR,         appointment, "primary"),
            ],
        ],
    }


def active_root(appointment) -> dict:
    """Кнопка «Управление записью»."""
    return {
        "one_time": False,
        "inline": False,
        "buttons": [[
            _btn("Управление записью", VK_CMD_MANAGE, appointment, "primary"),
        ]],
    }


def manage(appointment) -> dict:
    """Кнопки «Перенести» / «Отменить запись» / «Связь с врачом»."""
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                _btn("Перенести",        VK_CMD_RESCHEDULE_REQUEST, appointment, "primary"),
                _btn("Отменить запись",  VK_CMD_CANCEL_REQUEST,     appointment, "negative"),
            ],
            [
                _btn("Связь с врачом",   VK_CMD_DOCTOR,             appointment, "secondary"),
            ],
        ],
    }


def reschedule_options(appointment, slots) -> dict:
    """Свободные слоты для переноса по два в ряд и «Оставить как есть».
    Лимиты VK: до 5 кнопок в ряду и до 10 рядов."""
    buttons = [
        _btn(
            f"{slot.date:%d.%m} {slot.start_time:%H:%M}", VK_CMD_RESCHEDULE_TO, appointment, "primary", slot_id=slot.id
        )
        for slot in slots
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)][:8]
    rows.append([_btn("Оставить как есть", VK_CMD_CANCEL_KEEP, appointment, "secondary")])
    return {"one_time": False, "inline": False, "buttons": rows}


def cancel_confirm(appointment) -> dict:
    """Кнопки «Подтвердить отмену» / «Оставить запись»."""
    return {
        "one_time": False,
        "inline": False,
        "buttons": [[
            _btn("Подтвердить отмену", VK_CMD_CANCEL_CONFIRM, appointment, "negative"),
            _btn("Оставить запись",    VK_CMD_CANCEL_KEEP,    appointment, "secondary"),
        ]],
    }


def booking() -> dict:
    """Кнопка «Записаться онлайн» (ссылка на сайт)."""
    base_url = getattr(settings, "PUBLIC_BASE_URL", "https://doctor-barkova.ru").rstrip("/")
    return {
        "one_time": False,
        "inline": False,
        "buttons": [[
            {
                "action": {
                    "type": "open_link",
                    "label": "Записаться онлайн",
                    "link": f"{base_url}/booking",
                }
            }
        ]],
    }


def welcome(faq_items) -> dict:
    """Кнопки быстрых ответов (вопросы с короткой подписью из FAQ) и запись.

    Это обычные text-кнопки: при нажатии VK присылает message_new с payload.
    """
    base_url = getattr(settings, "PUBLIC_BASE_URL", "https://doctor-barkova.ru").rstrip("/")
    faq_buttons = [
        {
            "action": {
                "type": "text",
                "label": item.bot_label[:40],
                "payload": json.dumps({"cmd": VK_CMD_FAQ, "id": item.id}),
            },
            "color": "secondary",
        }
        for item in faq_items
    ]
    rows = [faq_buttons[i:i + 2] for i in range(0, len(faq_buttons), 2)][:4]
    rows.append([{"action": {"type": "open_link", "label": "Записаться онлайн", "link": f"{base_url}/booking"}}])
    return {"one_time": False, "inline": False, "buttons": rows}


def remove() -> dict:
    """Убирает клавиатуру."""
    return {"one_time": False, "inline": False, "buttons": []}

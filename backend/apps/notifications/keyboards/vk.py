"""
VK callback-клавиатуры для записей пациентов.
Единственный источник правды — дублирование из vk_bot.py устранено.
"""
from __future__ import annotations

import json

from apps.notifications.vk_constants import (
    VK_CMD_CONFIRM,
    VK_CMD_CANCEL_REQUEST,
    VK_CMD_YES,
    VK_CMD_DOCTOR,
    VK_CMD_MANAGE,
)

from django.conf import settings


def _btn(label: str, cmd: str, appointment, color: str) -> dict:
    return {
        "action": {
            "type": "callback",
            "label": label,
            "payload": json.dumps(
                {"cmd": cmd, "appointment_id": appointment.id, "token": appointment.vk_link_token},
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
    """Кнопки «Смогу» / «Не смогу» / «Связь с врачом» для напоминания."""
    return {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                _btn("Смогу",          VK_CMD_YES,           appointment, "positive"),
                _btn("Не смогу",       VK_CMD_CANCEL_REQUEST, appointment, "negative"),
            ],
            [
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
    """Кнопки «Отменить запись» / «Связь с врачом»."""
    return {
        "one_time": False,
        "inline": False,
        "buttons": [[
            _btn("Отменить запись",  VK_CMD_CANCEL_REQUEST, appointment, "negative"),
            _btn("Связь с врачом",   VK_CMD_DOCTOR,         appointment, "primary"),
        ]],
    }


def booking() -> dict:
    """Кнопка «Записаться онлайн» (ссылка на сайт)."""
    base_url = getattr(settings, "PUBLIC_BASE_URL", "https://doctor-barkova.ru")
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


def remove() -> dict:
    """Убирает клавиатуру."""
    return {"one_time": False, "inline": False, "buttons": []}

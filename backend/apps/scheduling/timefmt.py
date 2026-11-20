"""Форматирование времени слотов с явной подписью часового пояса.

Слоты хранятся как «дата + время» без пояса и трактуются в settings.TIME_ZONE.
Пациенты онлайн-разборов живут в разных городах, поэтому время везде
показываем с подписью вида «по времени Томска (МСК+4)».
"""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

_MOSCOW = ZoneInfo("Europe/Moscow")


def slot_start_datetime(slot_date: date, start_time: time) -> datetime:
    """Начало слота как aware-datetime в поясе расписания."""
    return timezone.make_aware(datetime.combine(slot_date, start_time), timezone.get_current_timezone())


def msk_offset_hours(at: datetime | None = None) -> int:
    """Разница пояса расписания с Москвой в часах (Томск: +4)."""
    at = at or timezone.now()
    local = at.astimezone(timezone.get_current_timezone()).utcoffset()
    moscow = at.astimezone(_MOSCOW).utcoffset()
    if local is None or moscow is None:
        return 0
    return int((local - moscow).total_seconds() // 3600)


def timezone_label() -> str:
    """«по времени Томска (МСК+4)» или «по московскому времени»."""
    offset = msk_offset_hours()
    if offset == 0:
        return "по московскому времени"
    sign = "+" if offset > 0 else "−"
    city = getattr(settings, "SCHEDULE_CITY_GENITIVE", "") or settings.TIME_ZONE
    return f"по времени {city} (МСК{sign}{abs(offset)})"

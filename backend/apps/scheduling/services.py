from collections.abc import Iterable
from datetime import date as date_type
from datetime import datetime, time, timedelta

from django.db.models import Count, Q
from django.utils import timezone

from .models import AvailabilityRule, DayException, TimeSlot

# ============================================================================
# Генерация слотов
# ============================================================================


def _generate_slots_for_day(
    target_date: date_type,
    start_time: time,
    end_time: time,
    slot_duration_min: int,
) -> list[TimeSlot]:
    """Создаёт TimeSlot'ы для одного дня и возвращает список созданных."""
    created = []
    current = datetime.combine(target_date, start_time)
    day_end = datetime.combine(target_date, end_time)

    while current + timedelta(minutes=slot_duration_min) <= day_end:
        next_end = current + timedelta(minutes=slot_duration_min)
        slot, was_created = TimeSlot.objects.get_or_create(
            date=target_date,
            start_time=current.time(),
            defaults={
                "end_time": next_end.time(),
                "is_booked": False,
                "is_active": True,
            },
        )
        if was_created:
            created.append(slot)
        current = next_end

    return created


def generate_slots_for_rule(rule: AvailabilityRule) -> list[TimeSlot]:
    """Создаёт слоты для всего диапазона правила, учитывая все weekdays."""
    created_slots: list[TimeSlot] = []
    weekdays = set(rule.effective_weekdays)
    if not weekdays:
        return created_slots

    # Все даты, на которые наложены DayException — пропускаем (если is_full_day)
    excluded_full = set(
        DayException.objects.filter(
            date__gte=rule.start_date,
            date__lte=rule.end_date,
            is_full_day=True,
        ).values_list("date", flat=True)
    )

    current_date = rule.start_date
    while current_date <= rule.end_date:
        if current_date.weekday() in weekdays and current_date not in excluded_full:
            created_slots.extend(
                _generate_slots_for_day(
                    current_date,
                    rule.start_time,
                    rule.end_time,
                    rule.slot_duration,
                )
            )
        current_date += timedelta(days=1)

    return created_slots


def generate_slots_for_rules(queryset: Iterable[AvailabilityRule]) -> list[TimeSlot]:
    total_created: list[TimeSlot] = []
    for rule in queryset:
        total_created.extend(generate_slots_for_rule(rule))
    return total_created


def generate_slots_bulk(
    start_date: date_type,
    end_date: date_type,
    weekdays: list[int],
    start_time: time,
    end_time: time,
    slot_duration_min: int,
) -> list[TimeSlot]:
    """
    Прямая bulk-генерация слотов без создания AvailabilityRule.
    Используется wizard-формой в админке.
    """
    if not weekdays:
        return []

    weekdays_set = set(weekdays)
    excluded_full = set(
        DayException.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_full_day=True,
        ).values_list("date", flat=True)
    )

    created: list[TimeSlot] = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() in weekdays_set and current_date not in excluded_full:
            created.extend(
                _generate_slots_for_day(
                    current_date,
                    start_time,
                    end_time,
                    slot_duration_min,
                )
            )
        current_date += timedelta(days=1)
    return created


# ============================================================================
# Запросы для фронта
# ============================================================================


BOOKING_CUTOFF = timedelta(hours=1)


def _bookable_q() -> Q:
    """Слоты, на которые ещё можно записаться: не раньше чем через час.

    Не полагаемся только на периодическую задачу deactivate_near_slots:
    между её запусками прошедшие слоты попадали в счётчики дат, и форма
    автоматически открывала сегодняшний день, в котором записаться уже некуда.
    """
    threshold = timezone.localtime(timezone.now() + BOOKING_CUTOFF)
    return Q(date__gt=threshold.date()) | Q(date=threshold.date(), start_time__gt=threshold.time())


def get_available_slots_queryset():
    return TimeSlot.objects.filter(
        _bookable_q(),
        is_booked=False,
        is_active=True,
    ).order_by("date", "start_time")


def get_nearest_available_slot():
    return get_available_slots_queryset().first()


def get_date_free_slots_count(target_date):
    return TimeSlot.objects.filter(
        _bookable_q(),
        date=target_date,
        is_booked=False,
        is_active=True,
    ).count()


def get_available_dates_with_counts():
    return (
        TimeSlot.objects.filter(
            _bookable_q(),
            is_booked=False,
            is_active=True,
        )
        .values("date")
        .annotate(free_slots=Count("id"))
        .order_by("date")
    )


# ============================================================================
# Открыть/закрыть конкретный день
# ============================================================================


def close_day_slots(target_date):
    """Делает все слоты дня недоступными (но не удаляет)."""
    return TimeSlot.objects.filter(
        date=target_date, is_active=True
    ).update(is_active=False)


def open_day_slots(target_date):
    return TimeSlot.objects.filter(date=target_date).update(is_active=True)


def apply_day_exception(exception: DayException) -> int:
    """
    Делает слоты в указанном дне неактивными согласно DayException.
    Возвращает количество затронутых слотов.
    """
    qs = TimeSlot.objects.filter(date=exception.date, is_booked=False)
    if not exception.is_full_day and exception.start_time and exception.end_time:
        qs = qs.filter(
            start_time__gte=exception.start_time,
            end_time__lte=exception.end_time,
        )
    return qs.update(is_active=False)

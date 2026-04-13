from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.utils import timezone

from .models import TimeSlot


def generate_slots_for_rule(rule):
    created_slots = []

    current_date = rule.start_date

    while current_date <= rule.end_date:
        if current_date.weekday() == rule.weekday:
            current_start = datetime.combine(current_date, rule.start_time)
            day_end = datetime.combine(current_date, rule.end_time)

            while current_start + timedelta(minutes=rule.slot_duration) <= day_end:
                current_end = current_start + timedelta(minutes=rule.slot_duration)

                slot, created = TimeSlot.objects.get_or_create(
                    date=current_date,
                    start_time=current_start.time(),
                    defaults={
                        "end_time": current_end.time(),
                        "is_booked": False,
                        "is_active": True,
                    },
                )

                if created:
                    created_slots.append(slot)

                current_start = current_end

        current_date += timedelta(days=1)

    return created_slots


def generate_slots_for_rules(queryset):
    total_created = []

    for rule in queryset:
        created_slots = generate_slots_for_rule(rule)
        total_created.extend(created_slots)

    return total_created


def get_available_slots_queryset():
    today = timezone.localdate()
    return TimeSlot.objects.filter(
        date__gte=today,
        is_booked=False,
        is_active=True,
    ).order_by("date", "start_time")


def get_nearest_available_slot():
    return get_available_slots_queryset().first()


def get_date_free_slots_count(target_date):
    return TimeSlot.objects.filter(
        date=target_date,
        is_booked=False,
        is_active=True,
    ).count()


def get_available_dates_with_counts():
    today = timezone.localdate()
    return (
        TimeSlot.objects.filter(
            date__gte=today,
            is_booked=False,
            is_active=True,
        )
        .values("date")
        .annotate(free_slots=Count("id"))
        .order_by("date")
    )


def close_day_slots(target_date):
    return TimeSlot.objects.filter(date=target_date, is_active=True).update(is_active=False)


def open_day_slots(target_date):
    return TimeSlot.objects.filter(date=target_date).update(is_active=True)

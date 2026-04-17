from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import TimeSlot


@shared_task
def deactivate_near_slots():
    now = timezone.now()
    threshold = now + timedelta(hours=1)

    slots = TimeSlot.objects.filter(
        is_active=True,
        is_booked=False,
        date__isnull=False,
    )

    updated_ids = []

    for slot in slots:
        slot_dt = timezone.make_aware(
            timezone.datetime.combine(slot.date, slot.start_time),
            timezone.get_current_timezone(),
        )
        if slot_dt <= threshold:
            slot.is_active = False
            slot.save(update_fields=["is_active"])
            updated_ids.append(slot.id)

    return {"updated_slot_ids": updated_ids, "count": len(updated_ids)}
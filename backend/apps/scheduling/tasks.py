from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import TimeSlot


@shared_task
def deactivate_near_slots():
    """
    Деактивирует слоты, до начала которых осталось менее 1 часа.

    Использует один UPDATE-запрос вместо Python-цикла с N сохранениями.
    Фильтр строится через аннотацию DateTimeField комбинацией даты и времени
    непосредственно на стороне БД.
    """
    now = timezone.now()
    threshold = now + timedelta(hours=1)

    # Конвертируем threshold в локальное время для сравнения с date+start_time
    local_tz = timezone.get_current_timezone()
    threshold_local = threshold.astimezone(local_tz)

    # Фильтр по дате + время: слот в прошлом или слишком близко.
    # Сначала отбираем по дате (дешёво), затем по времени.
    updated = TimeSlot.objects.filter(
        is_active=True,
        is_booked=False,
        date__lte=threshold_local.date(),
    ).exclude(
        # исключаем сегодняшние слоты, которые ещё далеко по времени
        date=threshold_local.date(),
        start_time__gt=threshold_local.time(),
    ).update(is_active=False)

    return {"count": updated}

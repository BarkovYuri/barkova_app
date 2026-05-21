"""Инвалидация кэша списков дат/слотов при изменении TimeSlot.

API-views в `views.py` кэшируют ответы на 60 секунд (это убирает 1-секундный
поход в БД на каждый запрос /api/available-dates и /api/available-slots).
Этот сигнал чистит кэш сразу же, как только администратор поменял слот
в админке или slot был забронирован — пациент видит свежую картину без
ожидания TTL.
"""

import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import TimeSlot

logger = logging.getLogger("apps.scheduling")


_DATES_KEY = "scheduling:available_dates"
_SLOTS_KEY_TMPL = "scheduling:available_slots:{date}"


@receiver(post_save, sender=TimeSlot)
@receiver(post_delete, sender=TimeSlot)
def invalidate_scheduling_cache(sender, instance: TimeSlot, **kwargs):
    cache.delete(_DATES_KEY)
    cache.delete(_SLOTS_KEY_TMPL.format(date=instance.date))
    logger.debug("scheduling cache invalidated for %s", instance.date)

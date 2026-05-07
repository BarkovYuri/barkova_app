import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .cache import PROFILE_CACHE_KEY
from .models import DoctorProfile

logger = logging.getLogger("apps.doctors")


@receiver(post_save, sender=DoctorProfile)
@receiver(post_delete, sender=DoctorProfile)
def invalidate_profile_cache(sender, **kwargs):
    cache.delete(PROFILE_CACHE_KEY)
    logger.info("DoctorProfile cache invalidated (%s)", kwargs.get("signal"))

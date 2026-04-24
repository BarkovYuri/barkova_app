import logging

from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DoctorProfile
from .serializers import DoctorProfileSerializer

logger = logging.getLogger("apps.doctors")

PROFILE_CACHE_KEY = "doctors:profile"
PROFILE_CACHE_TTL = 300  # 5 минут


class DoctorProfileView(APIView):
    def get(self, request):
        data = cache.get(PROFILE_CACHE_KEY)

        if data is None:
            profile = DoctorProfile.objects.first()
            if not profile:
                return Response(None)
            serializer = DoctorProfileSerializer(profile, context={"request": request})
            data = serializer.data
            cache.set(PROFILE_CACHE_KEY, data, timeout=PROFILE_CACHE_TTL)
            logger.debug("DoctorProfile loaded from DB and cached")
        else:
            logger.debug("DoctorProfile served from cache")

        return Response(data)
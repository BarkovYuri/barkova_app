import logging

from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import PROFILE_CACHE_KEY, PROFILE_CACHE_TTL
from .models import DoctorProfile
from .serializers import DoctorProfileSerializer

logger = logging.getLogger("apps.doctors")


class DoctorProfileView(APIView):
    def get(self, request):
        data = cache.get(PROFILE_CACHE_KEY)

        if data is None:
            profile = DoctorProfile.objects.first()
            if not profile:
                # 404, а не null со статусом 200: Next кэширует только ответы
                # 200, и пустой профиль застрял бы в кэше фронтенда.
                return Response(None, status=404)
            serializer = DoctorProfileSerializer(profile, context={"request": request})
            data = serializer.data
            cache.set(PROFILE_CACHE_KEY, data, timeout=PROFILE_CACHE_TTL)
            logger.debug("DoctorProfile loaded from DB and cached")
        else:
            logger.debug("DoctorProfile served from cache")

        return Response(data)

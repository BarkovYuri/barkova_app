from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DoctorProfile
from .serializers import DoctorProfileSerializer


class DoctorProfileView(APIView):
    def get(self, request):
        profile = DoctorProfile.objects.first()
        if not profile:
            return Response(None)

        serializer = DoctorProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)
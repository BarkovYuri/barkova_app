from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from apps.appointments.models import Appointment


class TelegramLinkView(APIView):
    def post(self, request):
        token = request.data.get("token")
        chat_id = request.data.get("chat_id")

        appointment = Appointment.objects.filter(
            telegram_link_token=token
        ).first()

        if not appointment:
            return Response({"error": "not found"}, status=404)

        appointment.telegram_chat_id = str(chat_id)
        appointment.telegram_linked_at = timezone.now()
        appointment.save()

        return Response({"status": "ok"})
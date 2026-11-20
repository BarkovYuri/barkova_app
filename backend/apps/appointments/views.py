import hmac
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.permissions import IsAdminUser
from apps.core.throttling import AppointmentCreateThrottle
from apps.notifications.tasks import process_vk_callback_event
from apps.notifications.transports import vk as vk_transport
from apps.notifications.vk_constants import (
    VK_EVENT_CONFIRMATION,
    VK_EVENT_MESSAGE_ALLOW,
    VK_EVENT_MESSAGE_EVENT,
    VK_EVENT_MESSAGE_NEW,
    VK_EVENT_MESSAGE_REPLY,
)
from apps.notifications.vk_serializers import VKCallbackEnvelopeSerializer

from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentPublicSerializer,
    AppointmentSerializer,
    AppointmentStatusUpdateSerializer,
)

logger = logging.getLogger("apps.appointments.views")

_HANDLED_VK_EVENTS = {
    VK_EVENT_MESSAGE_NEW,
    VK_EVENT_MESSAGE_EVENT,
    VK_EVENT_MESSAGE_REPLY,
    VK_EVENT_MESSAGE_ALLOW,
}


class AppointmentCreateView(CreateAPIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCreateSerializer
    throttle_classes = [AppointmentCreateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return Response(AppointmentPublicSerializer(appointment).data, status=status.HTTP_201_CREATED)


class AdminAppointmentListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = Appointment.objects.select_related("slot").prefetch_related("attachments").order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        date_param = self.request.query_params.get("date")
        if date_param:
            queryset = queryset.filter(slot__date=date_param)
        return queryset


class AdminAppointmentUpdateView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Appointment.objects.select_related("slot")
    serializer_class = AppointmentStatusUpdateSerializer


class VKMessagingStatusView(APIView):
    """Может ли сообщество писать пользователю. Форма записи опрашивает его
    после входа через VK ID, чтобы попросить разрешить сообщения."""

    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "vk_status"

    def get(self, request):
        vk_user_id = request.query_params.get("vk_user_id", "").strip()
        if not vk_user_id.isdigit():
            return Response({"detail": "vk_user_id обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        allowed, _ = vk_transport.is_messages_allowed(vk_user_id)
        return Response(
            {
                "vk_user_id": vk_user_id,
                "can_message_user": allowed,
                "dialog_url": vk_transport.community_dialog_url(),
            }
        )


class VKCallbackView(APIView):
    """Callback API сообщества. Отвечает VK сразу, обработку делает Celery."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VKCallbackEnvelopeSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse("ok")
        data = serializer.validated_data
        event_type = data["type"]

        expected_group = str(getattr(settings, "VK_GROUP_ID", "") or "")
        incoming_group = str(data.get("group_id") or "")
        if expected_group and incoming_group and incoming_group != expected_group:
            return HttpResponse("forbidden", status=403)

        if event_type == VK_EVENT_CONFIRMATION:
            return HttpResponse(settings.VK_CALLBACK_CONFIRMATION_CODE)

        # Без секрета эндпоинт не принимает события вообще. Сравнение
        # constant-time, чтобы не было timing-атаки.
        callback_secret = getattr(settings, "VK_CALLBACK_SECRET", "")
        incoming_secret = str(data.get("secret", "") or "")
        if not callback_secret or not hmac.compare_digest(incoming_secret, str(callback_secret)):
            return HttpResponse("forbidden", status=403)

        if event_type not in _HANDLED_VK_EVENTS:
            return HttpResponse("ok")

        event_id = data.get("event_id")
        cache_key = f"vk_callback_event:{event_id}" if event_id else ""
        # cache.add — атомарный SETNX: VK повторяет событие, если не получил
        # «ok» вовремя, и второй раз обрабатывать его не нужно.
        if cache_key and not cache.add(cache_key, "1", timeout=60 * 10):
            return HttpResponse("ok")

        try:
            process_vk_callback_event.delay(dict(request.data))
        except Exception:
            logger.exception("Failed to enqueue VK callback event %s", event_id)
            if cache_key:
                cache.delete(cache_key)
            # Не «ok» — VK повторит событие позже, и оно не потеряется.
            return HttpResponse("retry", status=503)

        return HttpResponse("ok")

import secrets

from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes

from apps.core.permissions import IsAdminUser
from apps.core.throttling import AppointmentCreateThrottle, PrelinkThrottle
from apps.notifications.models import TelegramPrelink, VKPrelink
from apps.notifications.services import (
    send_appointment_status_notification,
    send_doctor_contact_request_notification,
    send_to_patient,
    send_to_patient_vk,
    build_vk_booking_keyboard,
    build_vk_active_root_keyboard,
)
from apps.appointments.services.linking import (
    create_telegram_prelink,
    confirm_telegram_prelink,
    get_telegram_prelink_status,
    create_vk_prelink,
    confirm_vk_prelink,
    get_vk_prelink_status,
    create_vk_pending_link,
    resolve_vk_auto_link,
)
from apps.appointments.services.actions import AppointmentActionService
from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentStatusUpdateSerializer,
    QuickAppointmentCreateSerializer,
)

from apps.notifications.tasks import process_vk_callback_event
from apps.notifications.vk_serializers import VKCallbackEnvelopeSerializer
from apps.notifications.vk_constants import (
    VK_EVENT_CONFIRMATION,
    VK_EVENT_MESSAGE_NEW,
    VK_EVENT_MESSAGE_EVENT,
)


@authentication_classes([])
class AppointmentCreateView(CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCreateSerializer
    throttle_classes = [AppointmentCreateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        response_serializer = AppointmentSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@authentication_classes([])
class QuickAppointmentCreateView(APIView):
    throttle_classes = [AppointmentCreateThrottle]

    def post(self, request):
        serializer = QuickAppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        response_serializer = AppointmentSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AdminAppointmentListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = (
            Appointment.objects
            .select_related("slot")
            .prefetch_related("attachments")
            .order_by("-created_at")
        )

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        date_param = self.request.query_params.get("date")
        if date_param:
            queryset = queryset.filter(slot__date=date_param)

        return queryset


class AdminAppointmentUpdateView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentStatusUpdateSerializer


# =========================
# Telegram prelink
# =========================

@authentication_classes([])
class TelegramPrelinkCreateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PrelinkThrottle]

    def post(self, request):
        data = create_telegram_prelink(bot_username=settings.TELEGRAM_BOT_USERNAME)
        return Response(data, status=status.HTTP_201_CREATED)


@authentication_classes([])
class TelegramPrelinkLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token", "").strip()
        chat_id = str(request.data.get("chat_id", "")).strip()

        ok, error_msg = confirm_telegram_prelink(token, chat_id)
        if not ok:
            http_status = status.HTTP_400_BAD_REQUEST if "обязательны" in error_msg else status.HTTP_404_NOT_FOUND
            return Response({"detail": error_msg}, status=http_status)
        return Response({"status": "ok"})


@authentication_classes([])
class TelegramPrelinkStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token", "").strip()
        if not token:
            return Response({"detail": "token обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        result = get_telegram_prelink_status(token)
        if result is None:
            return Response({"detail": "Токен не найден."}, status=status.HTTP_404_NOT_FOUND)
        return Response(result)


@authentication_classes([])
class TelegramAppointmentActionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        token = request.data.get("token", "").strip()
        action = request.data.get("action", "").strip()
        chat_id = str(request.data.get("chat_id", "")).strip()

        if not appointment_id or not token or not action or not chat_id:
            return Response(
                {"detail": "appointment_id, token, action и chat_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = Appointment.objects.select_related("slot").filter(id=appointment_id).first()
        if not appointment:
            return Response({"detail": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)
        if appointment.telegram_link_token != token:
            return Response({"detail": "Неверный токен."}, status=status.HTTP_403_FORBIDDEN)
        if str(appointment.telegram_chat_id) != chat_id:
            return Response({"detail": "Неверный chat_id."}, status=status.HTTP_403_FORBIDDEN)

        result = AppointmentActionService.handle(appointment, action, channel="telegram")
        if "error" in result:
            return Response({"detail": "Неизвестное действие."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


# =========================
# VK prelink
# =========================

@authentication_classes([])
class VKPrelinkCreateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PrelinkThrottle]

    def post(self, request):
        data = create_vk_prelink(group_id=settings.VK_GROUP_ID)
        return Response(data, status=status.HTTP_201_CREATED)


@authentication_classes([])
class VKPrelinkLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token", "").strip()
        user_id = str(request.data.get("user_id", "")).strip()
        peer_id = str(request.data.get("peer_id", "")).strip()

        ok, error_msg = confirm_vk_prelink(token, user_id, peer_id)
        if not ok:
            http_status = status.HTTP_400_BAD_REQUEST if "обязательны" in error_msg else status.HTTP_404_NOT_FOUND
            return Response({"detail": error_msg}, status=http_status)
        return Response({"status": "ok"})


@authentication_classes([])
class VKPrelinkStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token", "").strip()
        if not token:
            return Response({"detail": "token обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        result = get_vk_prelink_status(token)
        if result is None:
            return Response({"detail": "Токен не найден."}, status=status.HTTP_404_NOT_FOUND)
        return Response(result)


@authentication_classes([])
class VKMessagingStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        vk_user_id = request.query_params.get("vk_user_id", "").strip()
        if not vk_user_id:
            return Response({"detail": "vk_user_id обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.notifications.services import _vk_is_messages_allowed
        allowed, error = _vk_is_messages_allowed(vk_user_id)
        dialog_url = f"https://vk.com/im?sel=-{settings.VK_GROUP_ID}"

        return Response({
            "vk_user_id": vk_user_id,
            "can_message_user": allowed,
            "error": error,
            "dialog_url": dialog_url,
        })


@authentication_classes([])
class VKPendingLinkCreateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PrelinkThrottle]

    def post(self, request):
        vk_user_id = str(request.data.get("vk_user_id", "")).strip()
        if not vk_user_id:
            return Response({"detail": "vk_user_id обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        data = create_vk_pending_link(vk_user_id=vk_user_id, group_id=settings.VK_GROUP_ID)
        return Response(data)


@authentication_classes([])
class VKAutoLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = str(request.data.get("user_id", "")).strip()
        peer_id = str(request.data.get("peer_id", "")).strip()
        if not user_id or not peer_id:
            return Response({"detail": "user_id и peer_id обязательны."}, status=status.HTTP_400_BAD_REQUEST)

        link_status = resolve_vk_auto_link(user_id=user_id, peer_id=peer_id)
        return Response({"status": link_status})


@authentication_classes([])
class VKAppointmentActionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        token = request.data.get("token", "").strip()
        action = request.data.get("action", "").strip()
        user_id = str(request.data.get("user_id", "")).strip()

        if not appointment_id or not token or not action or not user_id:
            return Response(
                {"detail": "appointment_id, token, action и user_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = Appointment.objects.select_related("slot").filter(id=appointment_id).first()
        if not appointment:
            return Response({"detail": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)
        if appointment.vk_link_token != token:
            return Response({"detail": "Неверный токен."}, status=status.HTTP_403_FORBIDDEN)
        if str(appointment.vk_user_id) != user_id:
            return Response({"detail": "Неверный user_id."}, status=status.HTTP_403_FORBIDDEN)

        result = AppointmentActionService.handle(appointment, action, channel="vk")
        if "error" in result:
            return Response({"detail": "Неизвестное действие."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        token = request.data.get("token", "").strip()
        action = request.data.get("action", "").strip()
        user_id = str(request.data.get("user_id", "")).strip()

        if not appointment_id or not token or not action or not user_id:
            return Response(
                {"detail": "appointment_id, token, action и user_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = Appointment.objects.select_related("slot").filter(id=appointment_id).first()
        if not appointment:
            return Response({"detail": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)
        if appointment.vk_link_token != token:
            return Response({"detail": "Неверный токен."}, status=status.HTTP_403_FORBIDDEN)
        if str(appointment.vk_user_id) != user_id:
            return Response({"detail": "Неверный user_id."}, status=status.HTTP_403_FORBIDDEN)

        result = AppointmentActionService.handle(appointment, action, channel="vk")
        if "error" in result:
            return Response({"detail": "Неизвестное действие."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        token = request.data.get("token", "").strip()
        action = request.data.get("action", "").strip()
        user_id = str(request.data.get("user_id", "")).strip()

        if not appointment_id or not token or not action or not user_id:
            return Response(
                {"detail": "appointment_id, token, action и user_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = Appointment.objects.select_related("slot").filter(id=appointment_id).first()
        if not appointment:
            return Response({"detail": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)
        if appointment.vk_link_token != token:
            return Response({"detail": "Неверный токен."}, status=status.HTTP_403_FORBIDDEN)
        if str(appointment.vk_user_id) != user_id:
            return Response({"detail": "Неверный user_id."}, status=status.HTTP_403_FORBIDDEN)

        result = AppointmentActionService.handle(appointment, action, channel="vk")
        if "error" in result:
            return Response({"detail": "Неизвестное действие."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        token = request.data.get("token", "").strip()
        action = request.data.get("action", "").strip()
        user_id = str(request.data.get("user_id", "")).strip()

        if not appointment_id or not token or not action or not user_id:
            return Response(
                {"detail": "appointment_id, token, action и user_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = Appointment.objects.select_related("slot").filter(id=appointment_id).first()
        if not appointment:
            return Response({"detail": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)
        if appointment.vk_link_token != token:
            return Response({"detail": "Неверный токен."}, status=status.HTTP_403_FORBIDDEN)
        if str(appointment.vk_user_id) != user_id:
            return Response({"detail": "Неверный user_id."}, status=status.HTTP_403_FORBIDDEN)

        result = AppointmentActionService.handle(appointment, action, channel="vk")
        if "error" in result:
            return Response({"detail": "Неизвестное действие."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


@authentication_classes([])
class VKCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VKCallbackEnvelopeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        event_type = data["type"]

        if event_type == VK_EVENT_CONFIRMATION:
            return HttpResponse(settings.VK_CALLBACK_CONFIRMATION_CODE)

        callback_secret = getattr(settings, "VK_CALLBACK_SECRET", "")
        incoming_secret = data.get("secret", "")
        # Если секрет не задан в настройках — отклоняем все запросы,
        # чтобы не открывать эндпоинт без защиты.
        if not callback_secret or incoming_secret != callback_secret:
            return HttpResponse("forbidden", status=403)

        if event_type not in {VK_EVENT_MESSAGE_NEW, VK_EVENT_MESSAGE_EVENT}:
            return HttpResponse("ok")

        event_id = data.get("event_id")
        if event_id:
            cache_key = f"vk_callback_event:{event_id}"
            if cache.get(cache_key):
                return HttpResponse("ok")
            cache.set(cache_key, "1", timeout=60 * 10)

        process_vk_callback_event.delay(data)

        return HttpResponse("ok")

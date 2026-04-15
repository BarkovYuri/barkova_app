import secrets

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
from apps.notifications.models import TelegramPrelink, VKPrelink
from apps.notifications.services import (
    send_appointment_status_notification,
    send_to_patient,
    send_to_patient_vk,
)
from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentStatusUpdateSerializer,
    QuickAppointmentCreateSerializer,
)


class AppointmentCreateView(CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        response_serializer = AppointmentSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class QuickAppointmentCreateView(APIView):
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

    def post(self, request):
        token = secrets.token_urlsafe(16)
        prelink = TelegramPrelink.objects.create(token=token)

        bot_username = settings.TELEGRAM_BOT_USERNAME
        bot_url = f"https://t.me/{bot_username}?start=connect_{token}"

        return Response(
            {
                "token": prelink.token,
                "bot_url": bot_url,
            },
            status=status.HTTP_201_CREATED,
        )


@authentication_classes([])
class TelegramPrelinkLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token", "").strip()
        chat_id = str(request.data.get("chat_id", "")).strip()

        if not token or not chat_id:
            return Response(
                {"detail": "token и chat_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prelink = TelegramPrelink.objects.filter(token=token, is_used=False).first()
        if not prelink:
            return Response(
                {"detail": "Токен не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        prelink.chat_id = chat_id
        prelink.linked_at = timezone.now()
        prelink.save(update_fields=["chat_id", "linked_at"])

        return Response({"status": "ok"})


@authentication_classes([])
class TelegramPrelinkStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token", "").strip()

        if not token:
            return Response(
                {"detail": "token обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prelink = TelegramPrelink.objects.filter(token=token).first()
        if not prelink:
            return Response(
                {"detail": "Токен не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "linked": bool(prelink.chat_id),
                "chat_id": prelink.chat_id,
            }
        )


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
            return Response(
                {"detail": "Запись не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if appointment.telegram_link_token != token:
            return Response(
                {"detail": "Неверный токен."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if str(appointment.telegram_chat_id) != chat_id:
            return Response(
                {"detail": "Неверный chat_id."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if action == "confirm":
            changed = appointment.status != "confirmed"

            if changed:
                appointment.status = "confirmed"
                appointment.save(update_fields=["status"])
                send_appointment_status_notification(appointment)

            send_to_patient(
                appointment,
                (
                    "✅ Запись подтверждена\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
            )
            return Response({"status": "confirmed"})

        if action == "cancel":
            changed = appointment.status != "cancelled"

            if changed:
                appointment.status = "cancelled"
                appointment.save(update_fields=["status"])

                slot = appointment.slot
                slot.is_booked = False
                slot.save(update_fields=["is_booked"])

                send_appointment_status_notification(appointment)

            send_to_patient(
                appointment,
                (
                    "❌ Запись отменена\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
            )
            return Response({"status": "cancelled"})

        return Response(
            {"detail": "Неизвестное действие."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================
# VK prelink
# =========================

@authentication_classes([])
class VKPrelinkCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = secrets.token_urlsafe(16)
        prelink = VKPrelink.objects.create(token=token)

        group_id = settings.VK_GROUP_ID
        vk_url = f"https://vk.com/im?sel=-{group_id}"

        return Response(
            {
                "token": prelink.token,
                "vk_url": vk_url,
            },
            status=status.HTTP_201_CREATED,
        )


@authentication_classes([])
class VKPrelinkLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token", "").strip()
        user_id = str(request.data.get("user_id", "")).strip()
        peer_id = str(request.data.get("peer_id", "")).strip()

        if not token or not user_id or not peer_id:
            return Response(
                {"detail": "token, user_id и peer_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prelink = VKPrelink.objects.filter(token=token, is_used=False).first()
        if not prelink:
            return Response(
                {"detail": "Токен не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        prelink.user_id = user_id
        prelink.peer_id = peer_id
        prelink.linked_at = timezone.now()
        prelink.save(update_fields=["user_id", "peer_id", "linked_at"])

        return Response({"status": "ok"})


@authentication_classes([])
class VKPrelinkStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token", "").strip()

        if not token:
            return Response(
                {"detail": "token обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prelink = VKPrelink.objects.filter(token=token).first()
        if not prelink:
            return Response(
                {"detail": "Токен не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "linked": bool(prelink.user_id and prelink.peer_id),
                "user_id": prelink.user_id,
                "peer_id": prelink.peer_id,
            }
        )


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
            return Response(
                {"detail": "Запись не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if appointment.vk_link_token != token:
            return Response(
                {"detail": "Неверный токен."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if str(appointment.vk_user_id) != user_id:
            return Response(
                {"detail": "Неверный user_id."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if action == "confirm":
            changed = appointment.status != "confirmed"

            if changed:
                appointment.status = "confirmed"
                appointment.save(update_fields=["status"])
                send_appointment_status_notification(appointment)

            send_to_patient_vk(
                appointment,
                (
                    "✅ Запись подтверждена\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
            )
            return Response({"status": "confirmed"})

        if action == "cancel":
            changed = appointment.status != "cancelled"

            if changed:
                appointment.status = "cancelled"
                appointment.save(update_fields=["status"])

                slot = appointment.slot
                slot.is_booked = False
                slot.save(update_fields=["is_booked"])

                send_appointment_status_notification(appointment)

            send_to_patient_vk(
                appointment,
                (
                    "❌ Запись отменена\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
            )
            return Response({"status": "cancelled"})

        return Response(
            {"detail": "Неизвестное действие."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@authentication_classes([])
class VKCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        if data.get("type") == "confirmation":
            return HttpResponse(settings.VK_CALLBACK_CONFIRMATION_CODE)

        if data.get("type") == "message_new":
            from vk_bot import handle_message_event
            handle_message_event(data)
            return HttpResponse("ok")

        return HttpResponse("ok")

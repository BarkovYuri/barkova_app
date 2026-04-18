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
from apps.notifications.models import TelegramPrelink, VKPrelink
from apps.notifications.services import (
    send_appointment_status_notification,
    send_doctor_contact_request_notification,
    send_to_patient,
    send_to_patient_vk,
    get_vk_remove_keyboard,
)
from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentStatusUpdateSerializer,
    QuickAppointmentCreateSerializer,
)


@authentication_classes([])
class AppointmentCreateView(CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        response_serializer = AppointmentSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@authentication_classes([])
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

            return Response({"status": "confirmed", "changed": changed})

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

            return Response({"status": "cancelled", "changed": changed})

        if action == "yes":
            appointment.reminder_response = "yes"
            appointment.reminder_response_at = timezone.now()
            appointment.save(update_fields=["reminder_response", "reminder_response_at"])

            send_to_patient(
                appointment,
                (
                    "✅ Отлично, ждём вас на консультации.\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
            )

            return Response({"status": "reminder_yes"})

        if action == "no":
            appointment.reminder_response = "no"
            appointment.reminder_response_at = timezone.now()

            changed = appointment.status != "cancelled"
            if changed:
                appointment.status = "cancelled"

            appointment.save(
                update_fields=["reminder_response", "reminder_response_at", "status"]
            )

            if changed:
                slot = appointment.slot
                slot.is_booked = False
                slot.save(update_fields=["is_booked"])
                send_appointment_status_notification(appointment)

            send_to_patient(
                appointment,
                (
                    "❌ Запись отменена по вашему ответу на напоминание.\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
            )

            return Response({"status": "reminder_no", "changed": changed})

        if action == "doctor":
            appointment.reminder_response = "doctor_contact"
            appointment.reminder_response_at = timezone.now()
            appointment.doctor_contact_requested_at = timezone.now()
            appointment.save(
                update_fields=[
                    "reminder_response",
                    "reminder_response_at",
                    "doctor_contact_requested_at",
                ]
            )

            send_doctor_contact_request_notification(appointment)

            send_to_patient(
                appointment,
                "💬 Передали врачу, что вам нужна связь. С вами свяжутся.",
            )

            return Response({"status": "doctor_contact_requested"})

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
class VKMessagingStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        vk_user_id = request.query_params.get("vk_user_id", "").strip()

        if not vk_user_id:
            return Response(
                {"detail": "vk_user_id обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверяем, можно ли писать пользователю
        from apps.notifications.services import _vk_is_messages_allowed

        allowed, error = _vk_is_messages_allowed(vk_user_id)

        group_id = settings.VK_GROUP_ID
        dialog_url = f"https://vk.com/im?sel=-{group_id}"

        return Response(
            {
                "vk_user_id": vk_user_id,
                "can_message_user": allowed,
                "error": error,
                "dialog_url": dialog_url,
            }
        )
    
@authentication_classes([])
class VKPendingLinkCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        vk_user_id = str(request.data.get("vk_user_id", "")).strip()

        if not vk_user_id:
            return Response(
                {"detail": "vk_user_id обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = f"vk_pending_link:{vk_user_id}"
        cache.set(cache_key, {"vk_user_id": vk_user_id}, timeout=15 * 60)

        group_id = settings.VK_GROUP_ID
        dialog_url = f"https://vk.com/im?sel=-{group_id}"

        return Response(
            {
                "status": "pending",
                "vk_user_id": vk_user_id,
                "dialog_url": dialog_url,
            }
        )

@authentication_classes([])
class VKAutoLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = str(request.data.get("user_id", "")).strip()
        peer_id = str(request.data.get("peer_id", "")).strip()

        if not user_id or not peer_id:
            return Response(
                {"detail": "user_id и peer_id обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = f"vk_pending_link:{user_id}"
        pending = cache.get(cache_key)

        if not pending:
            return Response({"status": "not_pending"})

        appointment = (
            Appointment.objects.filter(vk_user_id=user_id)
            .order_by("-created_at")
            .first()
        )

        if not appointment:
            return Response({"status": "no_appointment"})

        if appointment.vk_peer_id != peer_id:
            appointment.vk_peer_id = peer_id
            appointment.vk_linked_at = timezone.now()
            appointment.save(update_fields=["vk_peer_id", "vk_linked_at"])

        cache.delete(cache_key)

        return Response({"status": "linked"})


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
                keyboard=get_vk_remove_keyboard(),
            )

            return Response({"status": "confirmed", "changed": changed})

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
                keyboard=get_vk_remove_keyboard(),
            )

            return Response({"status": "cancelled", "changed": changed})

        if action == "yes":
            appointment.reminder_response = "yes"
            appointment.reminder_response_at = timezone.now()
            appointment.save(update_fields=["reminder_response", "reminder_response_at"])

            send_to_patient_vk(
                appointment,
                (
                    "✅ Отлично, ждём вас на консультации.\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
                keyboard=get_vk_remove_keyboard(),
            )

            return Response({"status": "reminder_yes"})

        if action == "no":
            appointment.reminder_response = "no"
            appointment.reminder_response_at = timezone.now()

            changed = appointment.status != "cancelled"
            if changed:
                appointment.status = "cancelled"

            appointment.save(
                update_fields=["reminder_response", "reminder_response_at", "status"]
            )

            if changed:
                slot = appointment.slot
                slot.is_booked = False
                slot.save(update_fields=["is_booked"])
                send_appointment_status_notification(appointment)

            send_to_patient_vk(
                appointment,
                (
                    "❌ Запись отменена по вашему ответу на напоминание.\n"
                    f"Дата: {appointment.slot.date}\n"
                    f"Время: {appointment.slot.start_time.strftime('%H:%M')}–"
                    f"{appointment.slot.end_time.strftime('%H:%M')}"
                ),
                keyboard=get_vk_remove_keyboard(),
            )

            return Response({"status": "reminder_no", "changed": changed})

        if action == "doctor":
            appointment.reminder_response = "doctor_contact"
            appointment.reminder_response_at = timezone.now()
            appointment.doctor_contact_requested_at = timezone.now()
            appointment.save(
                update_fields=[
                    "reminder_response",
                    "reminder_response_at",
                    "doctor_contact_requested_at",
                ]
            )

            send_doctor_contact_request_notification(appointment)

            send_to_patient_vk(
                appointment,
                "💬 Передали врачу, что вам нужна связь. С вами свяжутся.",
                keyboard=get_vk_remove_keyboard(),
            )

            return Response({"status": "doctor_contact_requested"})

        return Response(
            {"detail": "Неизвестное действие."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@authentication_classes([])
class VKCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        event_type = data.get("type")

        if event_type == "confirmation":
            return HttpResponse(settings.VK_CALLBACK_CONFIRMATION_CODE)

        if event_type == "message_new":
            from vk_bot import handle_new_message_event
            handle_new_message_event(data)
            return HttpResponse("ok")

        if event_type == "message_event":
            from vk_bot import handle_callback_event
            handle_callback_event(data)
            return HttpResponse("ok")

        return HttpResponse("ok")

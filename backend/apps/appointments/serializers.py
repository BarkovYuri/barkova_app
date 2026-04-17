from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.content.models import LegalDocument
from apps.notifications.models import TelegramPrelink, VKPrelink
from apps.notifications.services import (
    send_appointment_created_notification,
    send_appointment_status_notification,
    send_created_message_to_patient_with_actions,
    send_created_message_to_patient_with_actions_vk,
)
from apps.scheduling.models import TimeSlot
from .models import Appointment, AppointmentAttachment


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx", ".heic"}


def _validate_legal_flags(attrs):
    if not attrs.get("consent_given"):
        raise serializers.ValidationError(
            {"consent_given": "Необходимо согласие на обработку персональных данных."}
        )

    if not attrs.get("privacy_accepted"):
        raise serializers.ValidationError(
            {"privacy_accepted": "Необходимо принять политику конфиденциальности."}
        )

    if not attrs.get("offer_accepted"):
        raise serializers.ValidationError(
            {"offer_accepted": "Необходимо принять оферту."}
        )


def _get_available_slot_or_error(slot_id):
    from datetime import datetime, timedelta
    from django.utils import timezone

    try:
        slot = TimeSlot.objects.get(id=slot_id, is_active=True)
    except TimeSlot.DoesNotExist:
        raise serializers.ValidationError({"slot_id": "Слот не найден или недоступен."})

    if slot.is_booked:
        raise serializers.ValidationError({"slot_id": "Этот слот уже занят."})

    current_tz = timezone.get_current_timezone()
    slot_dt = timezone.make_aware(
        datetime.combine(slot.date, slot.start_time),
        current_tz,
    )
    threshold = timezone.now() + timedelta(hours=1)

    if slot_dt <= threshold:
        raise serializers.ValidationError(
            {"slot_id": "Запись на это время уже закрыта. Выберите слот позже чем через 1 час."}
        )

    return slot


def _get_active_legal_versions():
    offer_doc = (
        LegalDocument.objects.filter(doc_type="offer", is_active=True)
        .order_by("-created_at")
        .first()
    )
    privacy_doc = (
        LegalDocument.objects.filter(doc_type="privacy", is_active=True)
        .order_by("-created_at")
        .first()
    )
    consent_doc = (
        LegalDocument.objects.filter(doc_type="consent", is_active=True)
        .order_by("-created_at")
        .first()
    )

    return {
        "legal_offer_version": offer_doc.version if offer_doc else "",
        "legal_privacy_version": privacy_doc.version if privacy_doc else "",
        "legal_consent_version": consent_doc.version if consent_doc else "",
    }


def _normalize_telegram_username(value: str) -> str:
    value = value.strip()
    if value.startswith("@"):
        value = value[1:]
    return value


def _create_appointment_with_slot_lock(*, slot, appointment_data, files=None):
    import secrets

    files = files or []

    locked_slot = TimeSlot.objects.select_for_update().get(id=slot.id)

    if not locked_slot.is_active:
        raise serializers.ValidationError({"slot_id": "Этот слот недоступен для записи."})

    if locked_slot.is_booked:
        raise serializers.ValidationError({"slot_id": "Этот слот уже занят."})

    legal_versions = _get_active_legal_versions()

    try:
        appointment = Appointment.objects.create(
            slot=locked_slot,
            telegram_link_token=secrets.token_urlsafe(16),
            vk_link_token=secrets.token_urlsafe(16),
            **appointment_data,
            **legal_versions,
        )
    except IntegrityError:
        raise serializers.ValidationError(
            {"slot_id": "Этот слот уже только что заняли. Пожалуйста, выберите другое время."}
        )

    for file in files:
        AppointmentAttachment.objects.create(
            appointment=appointment,
            file=file,
        )

    locked_slot.is_booked = True
    locked_slot.save(update_fields=["is_booked"])

    def notify():
        appt = Appointment.objects.select_related("slot").prefetch_related("attachments").get(pk=appointment.pk)

        send_appointment_created_notification(appt)

        if appt.preferred_contact_method == "telegram" and appt.telegram_chat_id:
            send_created_message_to_patient_with_actions(appt)

        if appt.preferred_contact_method == "vk" and appt.vk_user_id:
            send_created_message_to_patient_with_actions_vk(appt)

    transaction.on_commit(notify)
    return appointment


class AppointmentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentAttachment
        fields = ["id", "file", "uploaded_at"]


class AppointmentSerializer(serializers.ModelSerializer):
    attachments = AppointmentAttachmentSerializer(many=True, read_only=True)
    slot_date = serializers.DateField(source="slot.date", read_only=True)
    slot_start_time = serializers.TimeField(source="slot.start_time", read_only=True)
    slot_end_time = serializers.TimeField(source="slot.end_time", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "slot",
            "slot_date",
            "slot_start_time",
            "slot_end_time",
            "name",
            "phone",
            "telegram_username",
            "preferred_contact_method",
            "telegram_link_token",
            "vk_link_token",
            "reason",
            "consent_given",
            "privacy_accepted",
            "offer_accepted",
            "legal_offer_version",
            "legal_privacy_version",
            "legal_consent_version",
            "status",
            "notes",
            "created_at",
            "attachments",
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    slot_id = serializers.IntegerField(write_only=True)
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    telegram_username = serializers.CharField(required=False, allow_blank=True)
    preferred_contact_method = serializers.ChoiceField(
        choices=["telegram", "vk"],
        required=False,
        allow_blank=True,
    )
    telegram_prelink_token = serializers.CharField(required=False, allow_blank=True)
    vk_prelink_token = serializers.CharField(required=False, allow_blank=True)
    vk_user_id = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "slot_id",
            "name",
            "phone",
            "telegram_username",
            "preferred_contact_method",
            "telegram_prelink_token",
            "vk_prelink_token",
            "vk_user_id",
            "reason",
            "consent_given",
            "privacy_accepted",
            "offer_accepted",
            "files",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Введите корректное имя.")
        return value

    def validate_phone(self, value):
        value = value.strip()

        allowed_chars = set("0123456789+() -")
        if any(char not in allowed_chars for char in value):
            raise serializers.ValidationError("Телефон может содержать только цифры, пробелы и символы +()-")

        digits_only = "".join(char for char in value if char.isdigit())
        if len(digits_only) < 10:
            raise serializers.ValidationError("Введите корректный номер телефона.")

        return value

    def validate_telegram_username(self, value):
        return _normalize_telegram_username(value)

    def validate_reason(self, value):
        return value.strip()

    def validate_files(self, files):
        for file in files:
            file_name = file.name.lower()
            if "." not in file_name:
                raise serializers.ValidationError(f"Файл {file.name} не имеет расширения.")

            extension = "." + file_name.rsplit(".", 1)[-1]
            if extension not in ALLOWED_EXTENSIONS:
                raise serializers.ValidationError(f"Формат файла {file.name} не поддерживается.")
        return files

    def validate(self, attrs):
        _validate_legal_flags(attrs)

        preferred_contact_method = attrs.get("preferred_contact_method", "").strip()
        telegram_prelink_token = attrs.get("telegram_prelink_token", "").strip()
        vk_prelink_token = attrs.get("vk_prelink_token", "").strip()
        vk_user_id = attrs.get("vk_user_id", "").strip()

        if preferred_contact_method == "telegram":
            if not telegram_prelink_token:
                raise serializers.ValidationError(
                    {"telegram_prelink_token": "Сначала подключите Telegram."}
                )

            prelink = TelegramPrelink.objects.filter(
                token=telegram_prelink_token,
                is_used=False,
            ).first()

            if not prelink or not prelink.chat_id:
                raise serializers.ValidationError(
                    {"telegram_prelink_token": "Telegram ещё не подключён."}
                )

            attrs["telegram_prelink"] = prelink

        if preferred_contact_method == "vk":
            if vk_user_id:
                attrs["vk_id_authorized"] = True
                attrs["vk_id_user_id"] = str(vk_user_id)

            elif vk_prelink_token:
                prelink = VKPrelink.objects.filter(
                    token=vk_prelink_token,
                    is_used=False,
                ).first()

                if not prelink or not prelink.user_id or not prelink.peer_id:
                    raise serializers.ValidationError(
                        {"vk_prelink_token": "VK ещё не подключён."}
                    )

                attrs["vk_prelink"] = prelink
            else:
                raise serializers.ValidationError(
                    {"vk_user_id": "Сначала войдите через VK ID."}
                )

        attrs["slot"] = _get_available_slot_or_error(attrs["slot_id"])
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        files = validated_data.pop("files", [])
        validated_data.pop("slot_id", None)
        slot = validated_data.pop("slot")

        telegram_prelink = validated_data.pop("telegram_prelink", None)
        vk_prelink = validated_data.pop("vk_prelink", None)
        vk_id_authorized = validated_data.pop("vk_id_authorized", False)
        vk_id_user_id = validated_data.pop("vk_id_user_id", "")

        validated_data.pop("telegram_prelink_token", None)
        validated_data.pop("vk_prelink_token", None)
        validated_data.pop("vk_user_id", None)

        appointment_data = {
            "name": validated_data["name"],
            "phone": validated_data["phone"],
            "telegram_username": validated_data.get("telegram_username", ""),
            "preferred_contact_method": validated_data.get("preferred_contact_method", ""),
            "telegram_chat_id": telegram_prelink.chat_id if telegram_prelink else "",
            "telegram_linked_at": telegram_prelink.linked_at if telegram_prelink else None,
            "vk_user_id": (
                vk_prelink.user_id if vk_prelink else (vk_id_user_id if vk_id_authorized else "")
            ),
            "vk_peer_id": vk_prelink.peer_id if vk_prelink else "",
            "vk_linked_at": vk_prelink.linked_at if vk_prelink else None,
            "reason": validated_data.get("reason", ""),
            "consent_given": validated_data["consent_given"],
            "privacy_accepted": validated_data["privacy_accepted"],
            "offer_accepted": validated_data["offer_accepted"],
        }

        appointment = _create_appointment_with_slot_lock(
            slot=slot,
            appointment_data=appointment_data,
            files=files,
        )

        if telegram_prelink:
            telegram_prelink.is_used = True
            telegram_prelink.save(update_fields=["is_used"])

        if vk_prelink:
            vk_prelink.is_used = True
            vk_prelink.save(update_fields=["is_used"])

        return appointment


class QuickAppointmentCreateSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=50)
    consent_given = serializers.BooleanField()
    privacy_accepted = serializers.BooleanField()
    offer_accepted = serializers.BooleanField()

    def validate_phone(self, value):
        value = value.strip()

        allowed_chars = set("0123456789+() -")
        if any(char not in allowed_chars for char in value):
            raise serializers.ValidationError("Телефон может содержать только цифры, пробелы и символы +()-")

        digits_only = "".join(char for char in value if char.isdigit())
        if len(digits_only) < 10:
            raise serializers.ValidationError("Введите корректный номер телефона.")

        return value

    def validate(self, attrs):
        _validate_legal_flags(attrs)
        attrs["slot"] = _get_available_slot_or_error(attrs["slot_id"])
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        slot = validated_data["slot"]

        appointment_data = {
            "name": "Быстрая запись",
            "phone": validated_data["phone"],
            "reason": "",
            "consent_given": validated_data["consent_given"],
            "privacy_accepted": validated_data["privacy_accepted"],
            "offer_accepted": validated_data["offer_accepted"],
        }

        return _create_appointment_with_slot_lock(
            slot=slot,
            appointment_data=appointment_data,
        )


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["status", "notes"]

    def validate_status(self, value):
        allowed_statuses = {"new", "confirmed", "completed", "cancelled"}
        if value not in allowed_statuses:
            raise serializers.ValidationError("Недопустимый статус.")
        return value

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", instance.status)

        instance.status = new_status
        instance.notes = validated_data.get("notes", instance.notes)
        instance.save()

        if old_status != "cancelled" and new_status == "cancelled":
            slot = instance.slot
            slot.is_booked = False
            slot.save(update_fields=["is_booked"])

        if old_status != new_status:
            transaction.on_commit(
                lambda: send_appointment_status_notification(
                    Appointment.objects.select_related("slot").get(pk=instance.pk)
                )
            )

        return instance

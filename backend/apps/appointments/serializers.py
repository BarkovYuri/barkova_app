from django.conf import settings
from django.db import transaction
from django.urls import reverse
from rest_framework import serializers

from apps.appointments.services.booking import (
    create_appointment_with_slot_lock,
    get_available_slot_or_error,
)
from apps.appointments.services.status import SOURCE_DOCTOR, change_status
from apps.notifications.services_vk_id import verify_vk_id_token

from .models import Appointment, AppointmentAttachment

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx", ".heic"}


def _validate_legal_flags(attrs):
    if not attrs.get("consent_given"):
        raise serializers.ValidationError({"consent_given": "Необходимо согласие на обработку персональных данных."})
    if not attrs.get("privacy_accepted"):
        raise serializers.ValidationError({"privacy_accepted": "Необходимо принять политику конфиденциальности."})
    if not attrs.get("offer_accepted"):
        raise serializers.ValidationError({"offer_accepted": "Необходимо принять оферту."})


def validate_phone_value(value: str) -> str:
    value = value.strip()
    allowed_chars = set("0123456789+() -")
    if any(char not in allowed_chars for char in value):
        raise serializers.ValidationError("Телефон может содержать только цифры, пробелы и символы +()-")
    digits_only = "".join(char for char in value if char.isdigit())
    if len(digits_only) < 10:
        raise serializers.ValidationError("Введите корректный номер телефона.")
    return value


class AppointmentAttachmentSerializer(serializers.ModelSerializer):
    """Файл пациента для API админки. Ссылка ведёт на защищённую выдачу,
    публичного URL у файлов нет."""

    url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentAttachment
        fields = ["id", "name", "url", "uploaded_at"]

    def get_url(self, obj):
        return reverse("protected-media", kwargs={"path": obj.file.name})

    def get_name(self, obj):
        return str(obj)


class AppointmentSerializer(serializers.ModelSerializer):
    """Полная запись — только для API админки."""

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
            "preferred_contact_method",
            "reason",
            "consent_given",
            "privacy_accepted",
            "offer_accepted",
            "legal_offer_version",
            "legal_privacy_version",
            "legal_consent_version",
            "status",
            "notes",
            "patient_notified_at",
            "created_at",
            "attachments",
        ]


class AppointmentPublicSerializer(serializers.ModelSerializer):
    """Ответ пациенту после записи: без файлов, заметок и служебных токенов."""

    slot_date = serializers.DateField(source="slot.date", read_only=True)
    slot_start_time = serializers.TimeField(source="slot.start_time", read_only=True)
    slot_end_time = serializers.TimeField(source="slot.end_time", read_only=True)

    class Meta:
        model = Appointment
        fields = ["id", "slot_date", "slot_start_time", "slot_end_time", "status", "created_at"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    slot_id = serializers.IntegerField(write_only=True)
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    # "vk" — подтверждение и напоминания в VK; "phone" — у пациента нет VK,
    # врач свяжется по телефону.
    preferred_contact_method = serializers.ChoiceField(choices=["vk", "phone"], required=False, allow_blank=True)
    vk_user_id = serializers.CharField(required=False, allow_blank=True)
    vk_id_access_token = serializers.CharField(required=False, allow_blank=True)
    # Soft-reservation токен. Если передан и валиден — освобождаем лок после
    # успешного create. Финальная защита от двойной записи — DB-constraint.
    reservation_token = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "slot_id",
            "name",
            "phone",
            "preferred_contact_method",
            "vk_user_id",
            "vk_id_access_token",
            "reservation_token",
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
        return validate_phone_value(value)

    def validate_reason(self, value):
        return value.strip()

    def validate_files(self, files):
        max_files = settings.APPOINTMENT_MAX_FILES
        max_mb = settings.APPOINTMENT_MAX_FILE_MB
        if len(files) > max_files:
            raise serializers.ValidationError(f"Можно приложить не больше {max_files} файлов.")
        for file in files:
            file_name = file.name.lower()
            if "." not in file_name:
                raise serializers.ValidationError(f"Файл {file.name} не имеет расширения.")
            extension = "." + file_name.rsplit(".", 1)[-1]
            if extension not in ALLOWED_EXTENSIONS:
                raise serializers.ValidationError(f"Формат файла {file.name} не поддерживается.")
            if file.size > max_mb * 1024 * 1024:
                raise serializers.ValidationError(f"Файл {file.name} больше {max_mb} МБ.")
        return files

    def validate(self, attrs):
        _validate_legal_flags(attrs)

        if attrs.get("preferred_contact_method", "").strip() == "vk":
            vk_user_id = attrs.get("vk_user_id", "").strip()
            vk_id_access_token = attrs.get("vk_id_access_token", "").strip()
            if not vk_user_id or not vk_id_access_token:
                raise serializers.ValidationError({"vk_user_id": "Сначала войдите через VK ID."})

            # VK ID 2.x использует PKCE: code обменивает браузерный SDK,
            # мы получаем готовый access_token и проверяем его у VK.
            result = verify_vk_id_token(access_token=vk_id_access_token, claimed_user_id=vk_user_id)
            if not result.get("verified"):
                raise serializers.ValidationError(
                    {"vk_user_id": "Не удалось подтвердить авторизацию VK ID. Войдите заново."}
                )
            attrs["verified_vk_user_id"] = result["user_id"]

        attrs["slot"] = get_available_slot_or_error(attrs["slot_id"])
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        files = validated_data.pop("files", [])
        slot = validated_data.pop("slot")
        reservation_token = validated_data.pop("reservation_token", "") or ""
        vk_user_id = validated_data.pop("verified_vk_user_id", "")

        appointment = create_appointment_with_slot_lock(
            slot=slot,
            appointment_data={
                "name": validated_data["name"],
                "phone": validated_data["phone"],
                "preferred_contact_method": validated_data.get("preferred_contact_method", ""),
                "vk_user_id": vk_user_id,
                "vk_peer_id": vk_user_id,
                "reason": validated_data.get("reason", ""),
                "consent_given": validated_data["consent_given"],
                "privacy_accepted": validated_data["privacy_accepted"],
                "offer_accepted": validated_data["offer_accepted"],
            },
            files=files,
        )

        # Best-effort освобождение soft-reservation: TTL всё равно истечёт.
        if reservation_token:
            from apps.scheduling.reservation import release_slot

            release_slot(slot.id, reservation_token)

        return appointment


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["status", "notes"]

    def update(self, instance, validated_data):
        if "notes" in validated_data:
            instance.notes = validated_data["notes"]
            instance.save(update_fields=["notes"])
        if "status" in validated_data:
            change_status(instance, validated_data["status"], source=SOURCE_DOCTOR)
        return instance

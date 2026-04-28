from django.db import transaction
from rest_framework import serializers

from apps.notifications.models import TelegramPrelink, VKPrelink
from apps.notifications.services import send_appointment_status_notification
from apps.appointments.services.booking import (
    get_available_slot_or_error as _get_available_slot_or_error,
    create_appointment_with_slot_lock as _create_appointment_with_slot_lock,
)
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


def _normalize_telegram_username(value: str) -> str:
    value = value.strip()
    if value.startswith("@"):
        value = value[1:]
    return value


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
    vk_id_code = serializers.CharField(required=False, allow_blank=True)
    vk_id_device_id = serializers.CharField(required=False, allow_blank=True)
    # Telegram WebApp Mini App: подписанная Telegram'ом строка с user data.
    # Если пришла валидная — пользователь автоматически привязан, prelink не нужен.
    tg_init_data = serializers.CharField(required=False, allow_blank=True)

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
            "vk_id_code",
            "vk_id_device_id",
            "tg_init_data",
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
            tg_init_data = attrs.get("tg_init_data", "").strip()

            # Сценарий A: пользователь зашёл из Mini App — initData валиден,
            # chat_id известен сразу, prelink не нужен.
            if tg_init_data:
                from apps.integrations.telegram_webapp import extract_telegram_user

                tg_user = extract_telegram_user(tg_init_data)
                if not tg_user:
                    raise serializers.ValidationError(
                        {"tg_init_data": "Не удалось проверить подпись Telegram."}
                    )
                attrs["telegram_webapp_user"] = tg_user
            # Сценарий B: классический flow через ссылку на бота
            elif telegram_prelink_token:
                prelink = TelegramPrelink.objects.filter(
                    token=telegram_prelink_token,
                    is_used=False,
                ).first()

                if not prelink or not prelink.chat_id:
                    raise serializers.ValidationError(
                        {"telegram_prelink_token": "Telegram ещё не подключён."}
                    )

                attrs["telegram_prelink"] = prelink
            else:
                raise serializers.ValidationError(
                    {"telegram_prelink_token": "Сначала подключите Telegram."}
                )

        if preferred_contact_method == "vk":
            vk_id_code = attrs.get("vk_id_code", "").strip()
            vk_id_device_id = attrs.get("vk_id_device_id", "").strip()

            if vk_id_code and vk_id_device_id:
                # Верифицируем VK ID через OAuth2 code exchange
                result = exchange_vk_id_code(code=vk_id_code, device_id=vk_id_device_id)

                if "error" in result or "access_token" not in result:
                    raise serializers.ValidationError(
                        {"vk_user_id": "Не удалось подтвердить авторизацию VK ID. Войдите заново."}
                    )

                verified_user_id = str(result.get("user_id", "")).strip()
                if not verified_user_id:
                    raise serializers.ValidationError(
                        {"vk_user_id": "VK ID не вернул идентификатор пользователя."}
                    )

                attrs["vk_id_authorized"] = True
                attrs["vk_id_user_id"] = verified_user_id

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
        telegram_webapp_user = validated_data.pop("telegram_webapp_user", None)
        vk_prelink = validated_data.pop("vk_prelink", None)
        vk_id_authorized = validated_data.pop("vk_id_authorized", False)
        vk_id_user_id = validated_data.pop("vk_id_user_id", "")

        validated_data.pop("telegram_prelink_token", None)
        validated_data.pop("vk_prelink_token", None)
        validated_data.pop("vk_user_id", None)
        validated_data.pop("vk_id_code", None)
        validated_data.pop("vk_id_device_id", None)
        validated_data.pop("tg_init_data", None)

        # Telegram chat_id и linked_at — из prelink ИЛИ из WebApp initData
        from django.utils import timezone

        if telegram_webapp_user:
            tg_chat_id = telegram_webapp_user["chat_id"]
            tg_linked_at = timezone.now()
            tg_username = telegram_webapp_user.get("username") or validated_data.get(
                "telegram_username", ""
            )
        elif telegram_prelink:
            tg_chat_id = telegram_prelink.chat_id
            tg_linked_at = telegram_prelink.linked_at
            tg_username = validated_data.get("telegram_username", "")
        else:
            tg_chat_id = ""
            tg_linked_at = None
            tg_username = validated_data.get("telegram_username", "")

        appointment_data = {
            "name": validated_data["name"],
            "phone": validated_data["phone"],
            "telegram_username": tg_username,
            "preferred_contact_method": validated_data.get("preferred_contact_method", ""),
            "telegram_chat_id": tg_chat_id,
            "telegram_linked_at": tg_linked_at,
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

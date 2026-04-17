from django.db import models
from apps.scheduling.models import TimeSlot


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("confirmed", "Подтверждена"),
        ("completed", "Завершена"),
        ("cancelled", "Отменена"),
    ]

    slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Слот времени",
    )
    name = models.CharField("Имя пациента", max_length=255)
    phone = models.CharField("Телефон", max_length=50)

    telegram_username = models.CharField("Telegram username", max_length=100, blank=True)

    preferred_contact_method = models.CharField(
        "Предпочтительный способ связи",
        max_length=20,
        choices=[
            ("telegram", "Telegram"),
            ("vk", "VK"),
        ],
        blank=True,
    )

    telegram_chat_id = models.CharField("Telegram chat id", max_length=50, blank=True)
    telegram_link_token = models.CharField("Telegram link token", max_length=64, blank=True)
    telegram_linked_at = models.DateTimeField("Telegram привязан", null=True, blank=True)

    vk_user_id = models.CharField("VK user id", max_length=50, blank=True)
    vk_peer_id = models.CharField("VK peer id", max_length=50, blank=True)
    vk_link_token = models.CharField("VK link token", max_length=64, blank=True)
    vk_linked_at = models.DateTimeField("VK привязан", null=True, blank=True)

    reminder_sent_at = models.DateTimeField("Напоминание отправлено", null=True, blank=True)

    reminder_response = models.CharField(
        "Ответ на напоминание",
        max_length=30,
        choices=[
            ("", "Нет ответа"),
            ("yes", "Смогу"),
            ("no", "Не смогу"),
            ("doctor_contact", "Связь с врачом"),
        ],
        blank=True,
        default="",
    )
    reminder_response_at = models.DateTimeField("Ответ на напоминание получен", null=True, blank=True)
    doctor_contact_requested_at = models.DateTimeField("Запрос связи с врачом", null=True, blank=True)

    reason = models.TextField("Причина обращения", blank=True)

    consent_given = models.BooleanField("Согласие на обработку данных")
    privacy_accepted = models.BooleanField("Политика конфиденциальности принята")
    offer_accepted = models.BooleanField("Оферта принята")

    legal_offer_version = models.CharField("Версия оферты", max_length=50, blank=True)
    legal_privacy_version = models.CharField("Версия политики", max_length=50, blank=True)
    legal_consent_version = models.CharField("Версия согласия", max_length=50, blank=True)

    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )
    notes = models.TextField("Заметки врача", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                condition=models.Q(status__in=["new", "confirmed"]),
                name="unique_active_appointment_per_slot",
            )
        ]
        verbose_name = "Запись пациента"
        verbose_name_plural = "Записи пациентов"

    def __str__(self):
        return f"{self.name} - {self.slot}"


class AppointmentAttachment(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Запись",
    )
    file = models.FileField("Файл", upload_to="appointments/")
    uploaded_at = models.DateTimeField("Загружен", auto_now_add=True)

    class Meta:
        verbose_name = "Файл пациента"
        verbose_name_plural = "Файлы пациента"

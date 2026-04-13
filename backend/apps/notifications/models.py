from django.db import models

from apps.appointments.models import Appointment


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ("telegram", "Telegram"),
        ("max", "Max"),
    ]

    TYPE_CHOICES = [
        ("created", "Создание записи"),
        ("reminder_3h", "Напоминание за 3 часа"),
        ("confirmed", "Подтверждение записи"),
        ("cancelled", "Отмена записи"),
    ]

    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("sent", "Отправлено"),
        ("failed", "Ошибка"),
    ]

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="notification_logs",
        verbose_name="Запись",
    )

    channel = models.CharField("Канал", max_length=20, choices=CHANNEL_CHOICES)
    notification_type = models.CharField(
        "Тип уведомления",
        max_length=30,
        choices=TYPE_CHOICES,
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    external_message_id = models.CharField("Внешний ID сообщения", max_length=255, blank=True)
    payload = models.JSONField("Payload", default=dict, blank=True)
    error_text = models.TextField("Текст ошибки", blank=True)

    scheduled_for = models.DateTimeField("Запланировано на", null=True, blank=True)
    sent_at = models.DateTimeField("Отправлено", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Лог уведомления"
        verbose_name_plural = "Логи уведомлений"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} / {self.get_channel_display()}"


class TelegramPrelink(models.Model):
    token = models.CharField("Токен привязки Telegram", max_length=64, unique=True)
    chat_id = models.CharField("Telegram chat id", max_length=50, blank=True)
    linked_at = models.DateTimeField("Привязан", null=True, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    is_used = models.BooleanField("Использован", default=False)

    class Meta:
        verbose_name = "Временная привязка Telegram"
        verbose_name_plural = "Временные привязки Telegram"
        ordering = ["-created_at"]

    def __str__(self):
        return self.token

class VKPrelink(models.Model):
    token = models.CharField("Токен привязки VK", max_length=64, unique=True)
    user_id = models.CharField("VK user id", max_length=50, blank=True)
    peer_id = models.CharField("VK peer id", max_length=50, blank=True)
    linked_at = models.DateTimeField("Привязан", null=True, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    is_used = models.BooleanField("Использован", default=False)

    class Meta:
        verbose_name = "Временная привязка VK"
        verbose_name_plural = "Временные привязки VK"
        ordering = ["-created_at"]

    def __str__(self):
        return self.token

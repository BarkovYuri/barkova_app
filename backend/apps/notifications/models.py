from django.db import models

from apps.appointments.models import Appointment


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ("vk", "VK"),
        ("email", "Email"),
        # Архивные каналы: остаются только для отображения старых записей лога.
        ("telegram", "Telegram (архив)"),
        ("max", "Max (архив)"),
    ]

    TYPE_CHOICES = [
        ("created", "Врачу: новая запись"),
        ("confirmed", "Врачу: запись подтверждена"),
        ("cancelled", "Врачу: запись отменена"),
        ("doctor_contact", "Врачу: просьба связаться"),
        ("rescheduled", "Врачу: запись перенесена"),
        ("incoming_message", "Врачу: входящее сообщение"),
        ("daily_digest", "Врачу: утренняя сводка"),
        ("patient_created", "Пациенту: запись создана"),
        ("patient_status", "Пациенту: смена статуса"),
        ("reminder", "Пациенту: напоминание"),
        ("reminder_3h", "Напоминание (архив)"),
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
        null=True,
        blank=True,
    )
    recipient = models.CharField("Получатель", max_length=255, blank=True)

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


class VKDialogState(models.Model):
    STATE_CHOICES = [
        ("idle", "Ожидание"),
        ("has_active_appointment", "Есть активная запись"),
        ("confirm_cancel", "Подтверждение отмены"),
    ]

    MENU_KIND_CHOICES = [
        ("none", "Нет меню"),
        ("booking", "Меню записи"),
        ("active_root", "Корневое меню активной записи"),
        ("manage", "Меню управления записью"),
        ("cancel_confirm", "Меню подтверждения отмены"),
    ]

    user_id = models.CharField("VK user id", max_length=50, unique=True)
    peer_id = models.CharField("VK peer id", max_length=50, blank=True)

    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vk_dialog_states",
    )

    state = models.CharField(
        "Состояние",
        max_length=50,
        choices=STATE_CHOICES,
        default="idle",
    )

    last_menu_kind = models.CharField(
        "Последнее меню",
        max_length=50,
        choices=MENU_KIND_CHOICES,
        default="none",
    )
    last_menu_sent_at = models.DateTimeField("Последнее меню отправлено", null=True, blank=True)
    last_action_at = models.DateTimeField("Последнее действие", null=True, blank=True)
    last_processed_event_id = models.CharField(
        "Последний обработанный event_id",
        max_length=120,
        blank=True,
        default="",
    )
    last_incoming_at = models.DateTimeField("Последнее входящее сообщение", null=True, blank=True)
    operator_paused_until = models.DateTimeField(
        "Бот молчит до",
        null=True,
        blank=True,
        help_text="Врач ответил в диалоге вручную, поэтому бот не вмешивается до этого времени.",
    )

    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Состояние VK-диалога"
        verbose_name_plural = "Состояния VK-диалогов"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user_id} / {self.state}"

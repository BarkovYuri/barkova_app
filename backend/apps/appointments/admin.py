import secrets
from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from rest_framework.exceptions import ValidationError as DRFValidationError
from unfold.admin import ModelAdmin, TabularInline

from apps.notifications.transports import vk as vk_transport

from .models import ACTIVE_STATUSES, Appointment, AppointmentAttachment
from .services.status import (
    SOURCE_DOCTOR,
    change_status,
    has_slot_conflict,
    schedule_status_notifications,
    sync_slot_booking,
)


def _protected_link(attachment: AppointmentAttachment) -> str:
    if not attachment.file:
        return "-"
    url = reverse("protected-media", kwargs={"path": attachment.file.name})
    return format_html('<a href="{}" target="_blank" rel="noopener">Открыть {}</a>', url, attachment)


class AppointmentAttachmentInline(TabularInline):
    model = AppointmentAttachment
    extra = 0
    fields = ("file_preview", "uploaded_at")
    readonly_fields = ("file_preview", "uploaded_at")
    can_delete = True

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Файл")
    def file_preview(self, obj):
        return _protected_link(obj)


class WhenFilter(admin.SimpleListFilter):
    """Быстрый взгляд на свой день: сегодня, завтра, предстоящие, прошедшие."""

    title = "Когда"
    parameter_name = "when"

    def lookups(self, request, model_admin):
        return [
            ("today", "Сегодня"),
            ("tomorrow", "Завтра"),
            ("upcoming", "Предстоящие"),
            ("past", "Прошедшие"),
        ]

    def queryset(self, request, queryset):
        today = timezone.localdate()
        value = self.value()
        if value == "today":
            return queryset.filter(slot__date=today).order_by("slot__start_time")
        if value == "tomorrow":
            return queryset.filter(slot__date=today + timedelta(days=1)).order_by("slot__start_time")
        if value == "upcoming":
            return queryset.filter(slot__date__gte=today, status__in=ACTIVE_STATUSES).order_by(
                "slot__date", "slot__start_time"
            )
        if value == "past":
            return queryset.filter(slot__date__lt=today)
        return queryset


class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"  # noqa: DJ007 — набор полей задают fieldsets админки

    def clean(self):
        cleaned = super().clean()
        slot = cleaned.get("slot")
        status = cleaned.get("status")
        if slot and status and has_slot_conflict(self.instance, slot.pk, status):
            raise forms.ValidationError(
                "На это время уже есть другая активная запись. Выберите другой слот или отмените ту запись."
            )
        return cleaned


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    form = AppointmentAdminForm

    list_display = (
        "id",
        "name",
        "phone",
        "slot_date",
        "slot_time",
        "status_colored",
        "contact_method",
        "vk_delivery",
        "has_files",
        "created_at",
    )
    list_filter = (WhenFilter, "status", "preferred_contact_method", "created_at", "slot__date")
    search_fields = ("name", "phone", "reason", "vk_user_id")
    ordering = ("-created_at",)
    list_select_related = ("slot",)
    actions = ["mark_confirmed", "mark_completed", "mark_cancelled"]
    inlines = [AppointmentAttachmentInline]

    fieldsets = (
        ("Пациент", {"fields": ("name", "phone", "reason")}),
        (
            "Связь",
            {
                "fields": (
                    "preferred_contact_method",
                    "vk_links",
                    "patient_notified_at",
                    "reminder_sent_at",
                    "reminder_response",
                    "doctor_contact_requested_at",
                )
            },
        ),
        ("Слот", {"fields": ("slot",)}),
        ("Согласия", {"fields": ("consent_given", "privacy_accepted", "offer_accepted")}),
        (
            "Статус",
            {
                "fields": ("status", "notes"),
                "description": "При подтверждении или отмене пациент получит сообщение в VK, "
                "а слот освободится или займётся автоматически.",
            },
        ),
    )
    readonly_fields = (
        "vk_links",
        "patient_notified_at",
        "reminder_sent_at",
        "reminder_response",
        "doctor_contact_requested_at",
    )

    # ===== Поля списка =====

    @admin.display(description="Дата", ordering="slot__date")
    def slot_date(self, obj):
        return obj.slot.date

    @admin.display(description="Время")
    def slot_time(self, obj):
        return f"{obj.slot.start_time:%H:%M}–{obj.slot.end_time:%H:%M}"

    @admin.display(description="Связь")
    def contact_method(self, obj):
        return obj.get_preferred_contact_method_display() or "-"

    @admin.display(description="VK-сообщение")
    def vk_delivery(self, obj):
        if obj.preferred_contact_method != "vk":
            return "-"
        return "✅" if obj.patient_notified_at else "⚠️ не доставлено"

    @admin.display(description="Файлы")
    def has_files(self, obj):
        return "📎" if obj.attachments.exists() else "-"

    @admin.display(description="Статус", ordering="status")
    def status_colored(self, obj):
        colors = {"new": "#3b82f6", "confirmed": "#22c55e", "completed": "#6b7280", "cancelled": "#ef4444"}
        return format_html('<b style="color:{};">{}</b>', colors.get(obj.status, "#000"), obj.get_status_display())

    @admin.display(description="VK пациента")
    def vk_links(self, obj):
        if not obj.vk_user_id:
            return "не привязан"
        peer = obj.vk_peer_id or obj.vk_user_id
        return format_html(
            '<a href="https://vk.com/id{}" target="_blank" rel="noopener">Профиль</a> · '
            '<a href="{}" target="_blank" rel="noopener">Открыть диалог</a>',
            obj.vk_user_id,
            vk_transport.admin_dialog_url(peer),
        )

    # ===== Сохранение из карточки =====

    def save_model(self, request, obj, form, change):
        old = Appointment.objects.filter(pk=obj.pk).values("slot_id", "status").first() if change else None
        if not obj.vk_link_token:
            # Токен нужен VK-кнопкам «подтвердить/отменить» и у записей,
            # созданных врачом вручную.
            obj.vk_link_token = secrets.token_urlsafe(16)
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            slot_ids = {obj.slot_id}
            if old:
                slot_ids.add(old["slot_id"])
            for slot_id in slot_ids:
                sync_slot_booking(slot_id)
            if old and old["status"] != obj.status:
                schedule_status_notifications(obj.pk, obj.status, SOURCE_DOCTOR)

    # ===== Массовые действия =====

    def _bulk_change(self, request, queryset, new_status: str, label: str):
        changed, skipped = 0, []
        for appointment in queryset.select_related("slot"):
            try:
                changed += int(change_status(appointment, new_status, source=SOURCE_DOCTOR))
            except DRFValidationError:
                skipped.append(str(appointment.pk))
        self.message_user(request, f"{label}: {changed}")
        if skipped:
            self.message_user(
                request,
                f"Не изменены (слот занят другой записью): {', '.join(skipped)}",
                level=messages.WARNING,
            )

    @admin.action(description="✅ Подтвердить запись (пациент получит сообщение)")
    def mark_confirmed(self, request, queryset):
        self._bulk_change(request, queryset.filter(status="new"), "confirmed", "Подтверждено записей")

    @admin.action(description="🏁 Отметить как завершённые")
    def mark_completed(self, request, queryset):
        self._bulk_change(request, queryset.filter(status__in=ACTIVE_STATUSES), "completed", "Завершено записей")

    @admin.action(description="❌ Отменить запись (слот освободится, пациент получит сообщение)")
    def mark_cancelled(self, request, queryset):
        self._bulk_change(request, queryset.exclude(status="cancelled"), "cancelled", "Отменено записей")


@admin.register(AppointmentAttachment)
class AppointmentAttachmentAdmin(ModelAdmin):
    list_display = ("appointment", "file_link", "uploaded_at")
    list_select_related = ("appointment",)

    @admin.display(description="Файл")
    def file_link(self, obj):
        return _protected_link(obj)

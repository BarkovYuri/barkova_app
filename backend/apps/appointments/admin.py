from django.contrib import admin
from django.utils.html import format_html

from .models import Appointment, AppointmentAttachment


# 📎 Inline файлы
class AppointmentAttachmentInline(admin.TabularInline):
    model = AppointmentAttachment
    extra = 0
    readonly_fields = ("file_preview",)

    def file_preview(self, obj):
        if not obj.file:
            return "-"
        return format_html(
            '<a href="{}" target="_blank">Открыть файл</a>',
            obj.file.url,
        )

    file_preview.short_description = "Файл"


# 👨‍⚕️ Основная админка
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    # 🔥 список
    list_display = (
        "id",
        "name",
        "phone",
        "slot_date",
        "slot_time",
        "status_colored",
        "contact_method",
        "has_files",
        "created_at",
    )

    # 🔍 фильтры
    list_filter = (
        "status",
        "preferred_contact_method",
        "created_at",
        "slot__date",
    )

    # 🔎 поиск
    search_fields = ("name", "phone", "reason")

    # 📊 сортировка
    ordering = ("-created_at",)

    # 📌 действия
    actions = ["mark_confirmed", "mark_cancelled"]

    # 📎 inline файлы
    inlines = [AppointmentAttachmentInline]

    # 📂 поля
    fieldsets = (
        ("Пациент", {
            "fields": ("name", "phone", "reason")
        }),
        ("Контакты", {
            "fields": (
                "preferred_contact_method",
                "telegram_username",
                "max_contact",
            )
        }),
        ("Слот", {
            "fields": ("slot",)
        }),
        ("Согласия", {
            "fields": ("consent_given", "privacy_accepted", "offer_accepted")
        }),
        ("Статус", {
            "fields": ("status", "notes")
        }),
    )

    # ===== КРАСИВЫЕ ПОЛЯ =====

    def slot_date(self, obj):
        return obj.slot.date

    slot_date.short_description = "Дата"

    def slot_time(self, obj):
        return f"{obj.slot.start_time.strftime('%H:%M')}–{obj.slot.end_time.strftime('%H:%M')}"

    slot_time.short_description = "Время"

    def contact_method(self, obj):
        return obj.preferred_contact_method or "-"

    contact_method.short_description = "Связь"

    def has_files(self, obj):
        return "📎" if obj.attachments.exists() else "-"

    has_files.short_description = "Файлы"

    def status_colored(self, obj):
        colors = {
            "new": "#3b82f6",
            "confirmed": "#22c55e",
            "completed": "#6b7280",
            "cancelled": "#ef4444",
        }
        color = colors.get(obj.status, "#000")

        return format_html(
            '<b style="color:{};">{}</b>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = "Статус"

    # ===== ДЕЙСТВИЯ =====

    @admin.action(description="✅ Подтвердить запись")
    def mark_confirmed(self, request, queryset):
        updated = queryset.exclude(status="confirmed").update(status="confirmed")
        self.message_user(request, f"Подтверждено записей: {updated}")

    @admin.action(description="❌ Отменить запись")
    def mark_cancelled(self, request, queryset):
        updated = queryset.exclude(status="cancelled").update(status="cancelled")

        # освобождаем слоты
        for appointment in queryset:
            if appointment.status != "cancelled":
                slot = appointment.slot
                slot.is_booked = False
                slot.save(update_fields=["is_booked"])

        self.message_user(request, f"Отменено записей: {updated}")


@admin.register(AppointmentAttachment)
class AppointmentAttachmentAdmin(admin.ModelAdmin):
    list_display = ("appointment", "uploaded_at")

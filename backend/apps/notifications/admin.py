from django.contrib import admin

from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "appointment",
        "channel",
        "notification_type",
        "status",
        "scheduled_for",
        "sent_at",
        "created_at",
    )
    list_filter = ("channel", "notification_type", "status", "created_at")
    search_fields = ("appointment__name", "appointment__phone", "external_message_id")

from django.contrib import admin

from .models import NotificationLog, VKDialogState


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


@admin.register(VKDialogState)
class VKDialogStateAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "peer_id",
        "state",
        "last_menu_kind",
        "appointment",
        "last_menu_sent_at",
        "last_action_at",
        "updated_at",
    )
    list_filter = ("state", "last_menu_kind", "updated_at")
    search_fields = ("user_id", "peer_id", "appointment__name", "appointment__phone")
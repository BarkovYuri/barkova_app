from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import NotificationLog, VKDialogState
from .transports import vk as vk_transport


@admin.register(NotificationLog)
class NotificationLogAdmin(ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "notification_type",
        "channel",
        "recipient",
        "status",
        "appointment",
    )
    list_filter = ("status", "channel", "notification_type", "created_at")
    search_fields = ("appointment__name", "appointment__phone", "recipient", "error_text")
    list_select_related = ("appointment",)
    readonly_fields = tuple(f.name for f in NotificationLog._meta.fields)

    def has_add_permission(self, request):
        return False


@admin.register(VKDialogState)
class VKDialogStateAdmin(ModelAdmin):
    list_display = (
        "user_id",
        "dialog_link",
        "last_incoming_at",
        "operator_paused_until",
        "last_menu_kind",
        "last_menu_sent_at",
        "appointment",
        "updated_at",
    )
    list_filter = ("state", "last_menu_kind", "updated_at")
    search_fields = ("user_id", "peer_id", "appointment__name", "appointment__phone")
    list_select_related = ("appointment",)

    @admin.display(description="Диалог")
    def dialog_link(self, obj):
        peer = obj.peer_id or obj.user_id
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Открыть</a>', vk_transport.admin_dialog_url(peer)
        )

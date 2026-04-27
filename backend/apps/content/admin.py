from django.contrib import admin

from .models import (
    ApproachItem,
    FaqItem,
    HowItWorksStep,
    LegalDocument,
    Service,
    SiteBlock,
    TrustBadge,
)


@admin.register(SiteBlock)
class SiteBlockAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "short_content", "updated_at")
    search_fields = ("key", "title", "content")
    ordering = ("key",)

    def short_content(self, obj):
        if not obj.content:
            return "—"
        return obj.content[:80] + ("…" if len(obj.content) > 80 else "")

    short_content.short_description = "Содержимое"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order", "id")
    fieldsets = (
        (None, {"fields": ("icon", "title", "description")}),
        ("Кнопка / ссылка", {"fields": ("cta_text", "cta_link")}),
        ("Отображение", {"fields": ("order", "is_active")}),
    )


@admin.register(HowItWorksStep)
class HowItWorksStepAdmin(admin.ModelAdmin):
    list_display = ("order_display", "title", "icon", "is_active", "updated_at")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order", "id")

    def order_display(self, obj):
        return f"#{obj.order}"

    order_display.short_description = "№"
    order_display.admin_order_field = "order"


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ("order", "question", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    ordering = ("order", "id")
    fieldsets = (
        (None, {"fields": ("question", "answer")}),
        ("Отображение", {"fields": ("order", "is_active")}),
    )


@admin.register(ApproachItem)
class ApproachItemAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order", "id")


@admin.register(TrustBadge)
class TrustBadgeAdmin(admin.ModelAdmin):
    list_display = ("label", "icon", "order", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("label",)
    ordering = ("order", "id")


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "doc_type", "version", "is_active", "created_at")
    list_filter = ("doc_type", "is_active")
    search_fields = ("title", "version")

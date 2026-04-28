from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    ApproachItem,
    FaqItem,
    HowItWorksStep,
    LegalDocument,
    Service,
    SiteBlock,
    TransportItem,
    TrustBadge,
)


PAGE_BY_PREFIX = {
    "hero.": "Главная (hero)",
    "services.": "Главная — Услуги",
    "how_it_works.": "Главная — Как это работает",
    "faq.": "Главная — FAQ",
    "cta.home.": "Главная — CTA",
    "approach.": "О враче — Подход",
    "cta.about.": "О враче — CTA",
    "office.": "Очный приём",
    "booking.": "Онлайн-запись",
    "contacts.": "Контакты",
}


def _page_for_key(key: str) -> str:
    for prefix, page in PAGE_BY_PREFIX.items():
        if key.startswith(prefix):
            return page
    return "Прочее"


class PageFilter(admin.SimpleListFilter):
    """Фильтр SiteBlock по разделу сайта (вычисляется из префикса ключа)."""

    title = "Раздел сайта"
    parameter_name = "page"

    def lookups(self, request, model_admin):
        return [(p, p) for p in sorted(set(PAGE_BY_PREFIX.values()))] + [
            ("__other__", "Прочее")
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        if value == "__other__":
            for prefix in PAGE_BY_PREFIX:
                queryset = queryset.exclude(key__startswith=prefix)
            return queryset
        prefixes = [p for p, page in PAGE_BY_PREFIX.items() if page == value]
        from django.db.models import Q

        q = Q()
        for prefix in prefixes:
            q |= Q(key__startswith=prefix)
        return queryset.filter(q)


@admin.register(SiteBlock)
class SiteBlockAdmin(ModelAdmin):
    list_display = ("page_display", "key", "title", "short_content", "updated_at")
    list_filter = (PageFilter,)
    search_fields = ("key", "title", "content")
    ordering = ("key",)

    @admin.display(description="Раздел сайта", ordering="key")
    def page_display(self, obj):
        return _page_for_key(obj.key)

    @admin.display(description="Содержимое")
    def short_content(self, obj):
        if not obj.content:
            return "—"
        return obj.content[:80] + ("…" if len(obj.content) > 80 else "")


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
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
class HowItWorksStepAdmin(ModelAdmin):
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
class FaqItemAdmin(ModelAdmin):
    list_display = ("question", "order", "is_active", "updated_at")
    list_display_links = ("question",)
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    ordering = ("order", "id")
    fieldsets = (
        (None, {"fields": ("question", "answer")}),
        ("Отображение", {"fields": ("order", "is_active")}),
    )


@admin.register(ApproachItem)
class ApproachItemAdmin(ModelAdmin):
    list_display = ("title", "icon", "order", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order", "id")


@admin.register(TrustBadge)
class TrustBadgeAdmin(ModelAdmin):
    list_display = ("label", "icon", "order", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("label",)
    ordering = ("order", "id")


@admin.register(TransportItem)
class TransportItemAdmin(ModelAdmin):
    list_display = ("title", "icon", "order", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order", "id")


@admin.register(LegalDocument)
class LegalDocumentAdmin(ModelAdmin):
    list_display = ("title", "doc_type", "version", "is_active", "created_at")
    list_filter = ("doc_type", "is_active")
    search_fields = ("title", "version")

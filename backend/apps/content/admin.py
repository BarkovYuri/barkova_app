from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    ApproachItem,
    Article,
    BlogCategory,
    ConditionCategory,
    ConditionItem,
    ConsultationFeature,
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


@admin.register(ConsultationFeature)
class ConsultationFeatureAdmin(ModelAdmin):
    list_display = (
        "title",
        "consultation_type",
        "icon",
        "order",
        "is_active",
        "updated_at",
    )
    list_editable = ("order", "is_active")
    list_filter = ("consultation_type", "is_active")
    search_fields = ("title", "description")
    ordering = ("consultation_type", "order", "id")
    fieldsets = (
        (None, {"fields": ("consultation_type", "icon", "title", "description")}),
        ("Отображение", {"fields": ("order", "is_active")}),
    )


class ConditionItemInline(TabularInline):
    model = ConditionItem
    extra = 1
    fields = ("text", "order", "is_active")
    ordering = ("order", "id")


@admin.register(ConditionCategory)
class ConditionCategoryAdmin(ModelAdmin):
    list_display = ("title", "icon", "order", "items_count", "is_active", "updated_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description", "items__text")
    ordering = ("order", "id")
    inlines = [ConditionItemInline]
    fieldsets = (
        (None, {"fields": ("icon", "title", "description")}),
        ("Отображение", {"fields": ("order", "is_active")}),
    )

    @admin.display(description="Пунктов")
    def items_count(self, obj):
        return obj.items.count()


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ("title", "is_published", "published_at", "updated_at")
    list_filter = ("is_published",)
    list_editable = ("is_published",)
    search_fields = ("title", "excerpt", "body", "keywords")
    ordering = ("-published_at", "-created_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "excerpt",
                    "body",
                ),
                "description": (
                    "Текст пишется в Markdown. Подсказка: ## заголовок, "
                    "**жирный**, *курсив*, [текст ссылки](https://...), "
                    "- пункт списка, > цитата."
                ),
            },
        ),
        (
            "Обложка",
            {"fields": ("cover", "cover_alt")},
        ),
        (
            "Публикация",
            {
                "fields": ("is_published", "published_at"),
                "description": (
                    "Поставьте «Опубликована», чтобы статья появилась "
                    "в /blog. Если дата пустая — поставится автоматически."
                ),
            },
        ),
        (
            "SEO (опционально)",
            {
                "fields": ("meta_title", "meta_description", "keywords"),
                "classes": ("collapse",),
            },
        ),
        (
            "Системное",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(BlogCategory)
class BlogCategoryAdmin(ModelAdmin):
    list_display = ("name", "is_active", "order", "articles_count", "updated_at")
    list_editable = ("is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("order", "id")
    filter_horizontal = ("articles",)
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "slug", "description"),
                "description": (
                    "Slug можно оставить пустым — сгенерируется автоматически "
                    "из названия. Описание показывается на странице кластера и "
                    "идёт в meta description, если SEO Description пуст."
                ),
            },
        ),
        ("Обложка", {"fields": ("cover", "cover_alt")}),
        (
            "Статьи",
            {
                "fields": ("articles",),
                "description": (
                    "Удерживайте Ctrl/Cmd для выбора нескольких статей. "
                    "Кнопками со стрелками можно переносить статьи между "
                    "«Доступные» и «Выбрано»."
                ),
            },
        ),
        ("Отображение", {"fields": ("is_active", "order")}),
        (
            "SEO (опционально)",
            {
                "fields": ("meta_title", "meta_description", "keywords"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ()

    @admin.display(description="Статей")
    def articles_count(self, obj):
        return obj.articles.count()


@admin.register(LegalDocument)
class LegalDocumentAdmin(ModelAdmin):
    list_display = ("title", "doc_type", "version", "is_active", "created_at")
    list_filter = ("doc_type", "is_active")
    search_fields = ("title", "version")

from rest_framework import serializers

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


class SiteBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteBlock
        fields = ["id", "key", "title", "content", "updated_at"]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "icon",
            "title",
            "description",
            "cta_text",
            "cta_link",
            "order",
        ]


class HowItWorksStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = HowItWorksStep
        fields = ["id", "icon", "title", "description", "order"]


class FaqItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqItem
        fields = ["id", "question", "answer", "order"]


class ApproachItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproachItem
        fields = ["id", "icon", "title", "description", "order"]


class TransportItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportItem
        fields = ["id", "icon", "title", "description", "order"]


class TrustBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustBadge
        fields = ["id", "icon", "label", "order"]


class ConsultationFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationFeature
        fields = ["id", "consultation_type", "icon", "title", "description", "order"]


class ConditionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionItem
        fields = ["id", "text", "order"]


class ConditionCategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = ConditionCategory
        fields = ["id", "icon", "title", "description", "order", "items"]

    def get_items(self, obj):
        active_items = [item for item in obj.items.all() if item.is_active]
        active_items.sort(key=lambda i: (i.order, i.id))
        return ConditionItemSerializer(active_items, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
    """Лёгкий сериализатор для /api/articles/ — без body."""

    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "cover_url",
            "cover_alt",
            "published_at",
            "views_count",
        ]

    def get_cover_url(self, obj):
        return obj.cover.url if obj.cover else None


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор для /api/articles/<slug>/ — с body."""

    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "body",
            "cover_url",
            "cover_alt",
            "published_at",
            "updated_at",
            "meta_title",
            "meta_description",
            "keywords",
            "views_count",
        ]

    def get_cover_url(self, obj):
        return obj.cover.url if obj.cover else None


class BlogCategoryListSerializer(serializers.ModelSerializer):
    """Лёгкий сериализатор для /api/blog-categories/ — без статей.

    Используется для grid-плашек на /blog. Дополнительно отдаём
    articles_count, чтобы можно было показать «N статей» на карточке.
    """

    cover_url = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "cover_url",
            "cover_alt",
            "articles_count",
        ]

    def get_cover_url(self, obj):
        return obj.cover.url if obj.cover else None

    def get_articles_count(self, obj):
        return getattr(obj, "_articles_count", obj.articles.filter(is_published=True).count())


class BlogCategoryDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор для /api/blog-categories/<slug>/ — со
    статьями кластера. Статьи рендерятся через ArticleListSerializer
    (без body, для карточек)."""

    cover_url = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "cover_url",
            "cover_alt",
            "meta_title",
            "meta_description",
            "keywords",
            "articles",
        ]

    def get_cover_url(self, obj):
        return obj.cover.url if obj.cover else None

    def get_articles(self, obj):
        active = (
            obj.articles.filter(is_published=True)
            .order_by("-published_at", "-created_at")
        )
        return ArticleListSerializer(active, many=True).data


class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = [
            "id",
            "doc_type",
            "title",
            "content",
            "version",
            "is_active",
            "created_at",
        ]

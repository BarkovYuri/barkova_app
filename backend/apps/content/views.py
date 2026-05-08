from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ApproachItem,
    Article,
    BlogCategory,
    ConditionCategory,
    ConsultationFeature,
    FaqItem,
    HowItWorksStep,
    LegalDocument,
    Service,
    SiteBlock,
    TransportItem,
    TrustBadge,
)
from .serializers import (
    ApproachItemSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    BlogCategoryDetailSerializer,
    BlogCategoryListSerializer,
    ConditionCategorySerializer,
    ConsultationFeatureSerializer,
    FaqItemSerializer,
    HowItWorksStepSerializer,
    LegalDocumentSerializer,
    ServiceSerializer,
    SiteBlockSerializer,
    TransportItemSerializer,
    TrustBadgeSerializer,
)


class SiteBlockListView(ListAPIView):
    """Все простые текстовые блоки (key/value)."""

    queryset = SiteBlock.objects.all().order_by("key")
    serializer_class = SiteBlockSerializer


class ActiveLegalDocumentListView(ListAPIView):
    serializer_class = LegalDocumentSerializer

    def get_queryset(self):
        return LegalDocument.objects.filter(is_active=True).order_by(
            "doc_type", "-created_at"
        )


class ServiceListView(ListAPIView):
    """Услуги (карточки на главной)."""

    serializer_class = ServiceSerializer

    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by("order", "id")


class HowItWorksStepListView(ListAPIView):
    """Шаги «Как это работает» на главной."""

    serializer_class = HowItWorksStepSerializer

    def get_queryset(self):
        return HowItWorksStep.objects.filter(is_active=True).order_by(
            "order", "id"
        )


class FaqItemListView(ListAPIView):
    """FAQ — частые вопросы."""

    serializer_class = FaqItemSerializer

    def get_queryset(self):
        return FaqItem.objects.filter(is_active=True).order_by("order", "id")


class ApproachItemListView(ListAPIView):
    """Пункты «Подход к работе» на странице «О враче»."""

    serializer_class = ApproachItemSerializer

    def get_queryset(self):
        return ApproachItem.objects.filter(is_active=True).order_by(
            "order", "id"
        )


class TrustBadgeListView(ListAPIView):
    """Бейджи доверия (под hero)."""

    serializer_class = TrustBadgeSerializer

    def get_queryset(self):
        return TrustBadge.objects.filter(is_active=True).order_by("order", "id")


class TransportItemListView(ListAPIView):
    """Способы добраться на /office."""

    serializer_class = TransportItemSerializer

    def get_queryset(self):
        return TransportItem.objects.filter(is_active=True).order_by(
            "order", "id"
        )


class ConsultationFeatureListView(ListAPIView):
    """«Что входит» — для /booking (?type=online) и /office (?type=office)."""

    serializer_class = ConsultationFeatureSerializer

    def get_queryset(self):
        qs = ConsultationFeature.objects.filter(is_active=True).order_by(
            "order", "id"
        )
        consultation_type = self.request.query_params.get("type")
        if consultation_type in {"online", "office"}:
            qs = qs.filter(consultation_type=consultation_type)
        return qs


class ArticleListView(ListAPIView):
    """Список опубликованных статей блога."""

    serializer_class = ArticleListSerializer

    def get_queryset(self):
        return Article.objects.filter(is_published=True).order_by(
            "-published_at", "-created_at"
        )


class ArticleDetailView(RetrieveAPIView):
    """Одна статья по slug. Используется на /blog/[slug]."""

    serializer_class = ArticleDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Article.objects.filter(is_published=True)


class BlogCategoryListView(ListAPIView):
    """Список активных кластеров блога — для grid-плашек на /blog."""

    serializer_class = BlogCategoryListSerializer

    def get_queryset(self):
        return (
            BlogCategory.objects.filter(is_active=True)
            .prefetch_related("articles")
            .order_by("order", "id")
        )


class BlogCategoryDetailView(RetrieveAPIView):
    """Один кластер по slug, с вложенным списком опубликованных статей."""

    serializer_class = BlogCategoryDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            BlogCategory.objects.filter(is_active=True)
            .prefetch_related("articles")
        )


class ArticleViewIncrementView(APIView):
    """Атомарный инкремент счётчика просмотров.

    Защита от накрутки на стороне фронта: один инкремент за сессию
    (sessionStorage). На бэке дополнительно стоит scope-throttle
    «article_view» — 60 инкрементов в час с одного IP.
    """

    throttle_scope = "article_view"

    def post(self, request, slug: str):
        article = get_object_or_404(Article, slug=slug, is_published=True)
        Article.objects.filter(pk=article.pk).update(
            views_count=F("views_count") + 1
        )
        article.refresh_from_db(fields=["views_count"])
        return Response(
            {"slug": article.slug, "views_count": article.views_count},
            status=status.HTTP_200_OK,
        )


class ConditionCategoryListView(ListAPIView):
    """«С чем можно обратиться» — для /about (с вложенными items)."""

    serializer_class = ConditionCategorySerializer

    def get_queryset(self):
        return (
            ConditionCategory.objects.filter(is_active=True)
            .prefetch_related("items")
            .order_by("order", "id")
        )

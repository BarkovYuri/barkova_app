from rest_framework.generics import ListAPIView

from .models import (
    ApproachItem,
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


class ConditionCategoryListView(ListAPIView):
    """«С чем можно обратиться» — для /about (с вложенными items)."""

    serializer_class = ConditionCategorySerializer

    def get_queryset(self):
        return (
            ConditionCategory.objects.filter(is_active=True)
            .prefetch_related("items")
            .order_by("order", "id")
        )

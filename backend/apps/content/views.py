from rest_framework.generics import ListAPIView

from .models import (
    ApproachItem,
    FaqItem,
    HowItWorksStep,
    LegalDocument,
    Service,
    SiteBlock,
    TrustBadge,
)
from .serializers import (
    ApproachItemSerializer,
    FaqItemSerializer,
    HowItWorksStepSerializer,
    LegalDocumentSerializer,
    ServiceSerializer,
    SiteBlockSerializer,
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

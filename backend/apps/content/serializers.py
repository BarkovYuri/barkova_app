from rest_framework import serializers

from .models import (
    ApproachItem,
    FaqItem,
    HowItWorksStep,
    LegalDocument,
    Service,
    SiteBlock,
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


class TrustBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustBadge
        fields = ["id", "icon", "label", "order"]


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

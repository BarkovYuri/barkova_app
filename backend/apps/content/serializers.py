from rest_framework import serializers
from .models import SiteBlock, LegalDocument


class SiteBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteBlock
        fields = [
            "id",
            "key",
            "title",
            "content",
            "updated_at",
        ]


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

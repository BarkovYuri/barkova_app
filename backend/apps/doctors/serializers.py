from rest_framework import serializers

from apps.core.images import AVATAR_SIZE, variant_url

from .models import DoctorProfile


class DoctorProfileSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    header_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "full_name",
            "photo",
            "photo_url",
            "header_avatar",
            "header_avatar_url",
            "short_intro",
            "description",
            "education",
            "experience_years",
            "prodoktorov_url",
            "prodoktorov_rating",
            "prodoktorov_reviews_count",
            "address",
            "phone",
            "email",
            "instagram_url",
            "dzen_url",
            "vk_url",
            "yandex_maps_embed_url",
            "updated_at",
        ]

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_header_avatar_url(self, obj):
        # Шапка и блок автора показывают аватар 40–56 px: отдаём квадратную
        # копию 128 px вместо оригинала 720×1080.
        source = obj.header_avatar or obj.photo
        return variant_url(source, AVATAR_SIZE, square=True) if source else None

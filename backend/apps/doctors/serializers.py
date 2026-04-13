from rest_framework import serializers
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
            "description",
            "education",
            "experience_years",
            "prodoktorov_url",
            "address",
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
        if obj.header_avatar:
            return obj.header_avatar.url
        return None

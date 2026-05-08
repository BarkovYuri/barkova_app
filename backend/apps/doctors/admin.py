from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(ModelAdmin):
    list_display = ("full_name", "experience_years", "email", "updated_at")
    search_fields = ("full_name", "email")
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "full_name",
                    "photo",
                    "header_avatar",
                    "short_intro",
                    "description",
                    "education",
                    "experience_years",
                )
            },
        ),
        (
            "Очный прием",
            {
                "fields": (
                    "address",
                    "yandex_maps_embed_url",
                )
            },
        ),
        (
            "ПроДокторов",
            {
                "fields": (
                    "prodoktorov_url",
                    "prodoktorov_rating",
                    "prodoktorov_reviews_count",
                ),
                "description": (
                    "Если отзывы есть на ПроДокторов — заполните рейтинг и "
                    "количество. Это покажет звёздочки на главной и в "
                    "результатах поиска Google."
                ),
            },
        ),
        (
            "Контакты и соцсети",
            {
                "fields": (
                    "phone",
                    "email",
                    "instagram_url",
                    "vk_url",
                    "dzen_url",
                )
            },
        ),
    )

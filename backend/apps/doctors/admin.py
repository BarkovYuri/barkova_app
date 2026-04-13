from django.contrib import admin
from .models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
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
                    "prodoktorov_url",
                    "yandex_maps_embed_url",
                )
            },
        ),
        (
            "Контакты и соцсети",
            {
                "fields": (
                    "email",
                    "instagram_url",
                    "vk_url",
                    "dzen_url",
                )
            },
        ),
    )

from django.db import models


class DoctorProfile(models.Model):
    full_name = models.CharField("ФИО", max_length=255)
    photo = models.ImageField("Основное фото", upload_to="doctor/", blank=True, null=True)
    header_avatar = models.ImageField(
        "Аватар для шапки",
        upload_to="doctor/header/",
        blank=True,
        null=True,
    )

    short_intro = models.CharField(
        "Короткое описание (для главной)",
        max_length=500,
        blank=True,
        help_text=(
            "Одно-два предложения для hero на главной странице. "
            "Если оставить пустым — на главной будет показан первый "
            "абзац из «Полного описания»."
        ),
    )
    description = models.TextField(
        "Полное описание (для страницы «О враче»)",
        blank=True,
        help_text=(
            "Длинный текст с абзацами. Отображается на /about. "
            "На главной целиком НЕ показывается — для главной используйте "
            "поле «Короткое описание» выше."
        ),
    )
    education = models.TextField("Образование", blank=True)

    experience_years = models.PositiveIntegerField("Стаж", default=0)

    prodoktorov_url = models.URLField("Ссылка на ПроДокторов", blank=True)
    address = models.CharField("Адрес приема", max_length=255, blank=True)
    phone = models.CharField(
        "Телефон",
        max_length=50,
        blank=True,
        help_text="В международном формате, например +7 (3822) 123-45-67. "
        "На странице «Контакты» отобразится как кликабельная ссылка tel:.",
    )
    email = models.EmailField("Email", blank=True)

    instagram_url = models.URLField("Ссылка на Instagram", blank=True)
    dzen_url = models.URLField("Ссылка на Дзен", blank=True)
    vk_url = models.URLField("Ссылка на VK", blank=True)

    yandex_maps_embed_url = models.URLField(
        "Ссылка для встроенной Яндекс.Карты",
        blank=True,
        help_text="Сюда вставляется именно embed/iframe ссылка для отображения карты на сайте.",
    )

    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Профиль врача"
        verbose_name_plural = "Профили врача"

    def __str__(self):
        return self.full_name

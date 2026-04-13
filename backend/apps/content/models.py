from django.db import models


class SiteBlock(models.Model):
    key = models.CharField("Ключ блока", max_length=100, unique=True)
    title = models.CharField("Заголовок", max_length=255, blank=True)
    content = models.TextField("Контент", blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Блок сайта"
        verbose_name_plural = "Блоки сайта"

    def __str__(self):
        return self.key


class LegalDocument(models.Model):
    DOCUMENT_TYPES = [
        ("offer", "Оферта"),
        ("privacy", "Политика конфиденциальности"),
        ("consent", "Согласие на обработку данных"),
    ]

    doc_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()

    version = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Юридический документ"
        verbose_name_plural = "Юридические документы"

    def __str__(self):
        return f"{self.title} (v{self.version})"

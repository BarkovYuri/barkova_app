from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0008_article_views_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text=(
                            "Латиницей через дефисы. Можно оставить пустым — "
                            "сгенерируется автоматически из названия через транслит."
                        ),
                        max_length=255,
                        unique=True,
                        verbose_name="URL (slug)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "Показывается на странице кластера под заголовком и "
                            "используется как meta description в выдаче Google."
                        ),
                        verbose_name="Краткое описание",
                    ),
                ),
                (
                    "cover",
                    models.ImageField(
                        blank=True,
                        help_text="Если оставить пустым — карточка покажется с градиентом.",
                        null=True,
                        upload_to="blog/categories/",
                        verbose_name="Обложка",
                    ),
                ),
                (
                    "cover_alt",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Alt-текст обложки",
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Чем меньше — тем выше в списке кластеров.",
                        verbose_name="Порядок",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Показывать на сайте"),
                ),
                (
                    "meta_title",
                    models.CharField(blank=True, max_length=255, verbose_name="SEO Title (опц)"),
                ),
                (
                    "meta_description",
                    models.CharField(
                        blank=True, max_length=300, verbose_name="SEO Description (опц)"
                    ),
                ),
                (
                    "keywords",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        verbose_name="Ключевые слова (через запятую)",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "articles",
                    models.ManyToManyField(
                        blank=True,
                        related_name="categories",
                        to="content.article",
                        verbose_name="Статьи в кластере",
                    ),
                ),
            ],
            options={
                "verbose_name": "Кластер блога",
                "verbose_name_plural": "Кластеры блога",
                "ordering": ["order", "id"],
            },
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0006_replace_konsultatsia_in_db"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
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
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text=(
                            "Латиницей через дефисы. Можно оставить пустым — "
                            "сгенерируется автоматически из заголовка через транслит."
                        ),
                        max_length=255,
                        unique=True,
                        verbose_name="URL (slug)",
                    ),
                ),
                (
                    "excerpt",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "1-2 предложения для карточки в списке статей и для meta "
                            "description в поисковой выдаче."
                        ),
                        max_length=500,
                        verbose_name="Краткое описание (превью)",
                    ),
                ),
                (
                    "body",
                    models.TextField(
                        help_text=(
                            "Поддерживается Markdown: ## Заголовок, **жирный**, *курсив*, "
                            "[ссылка](https://...), списки, переносы строк, цитаты."
                        ),
                        verbose_name="Текст статьи (Markdown)",
                    ),
                ),
                (
                    "cover",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="blog/",
                        verbose_name="Обложка",
                    ),
                ),
                (
                    "cover_alt",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Alt-текст обложки (для SEO)",
                    ),
                ),
                (
                    "is_published",
                    models.BooleanField(
                        default=False,
                        help_text="Если выключено — статья не показывается на сайте.",
                        verbose_name="Опубликована",
                    ),
                ),
                (
                    "published_at",
                    models.DateTimeField(
                        blank=True,
                        help_text=(
                            "Если оставить пустым — поставится автоматически при первой "
                            "публикации. Можно поставить дату вручную для backdate'инга."
                        ),
                        null=True,
                        verbose_name="Дата публикации",
                    ),
                ),
                (
                    "meta_title",
                    models.CharField(
                        blank=True,
                        help_text="Если пусто — берётся обычный заголовок.",
                        max_length=255,
                        verbose_name="SEO Title (опц)",
                    ),
                ),
                (
                    "meta_description",
                    models.CharField(
                        blank=True,
                        help_text="Если пусто — берётся «Краткое описание».",
                        max_length=300,
                        verbose_name="SEO Description (опц)",
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
            ],
            options={
                "verbose_name": "Статья блога",
                "verbose_name_plural": "Статьи блога",
                "ordering": ["-published_at", "-created_at"],
                "indexes": [
                    models.Index(
                        fields=["is_published", "-published_at"],
                        name="content_art_is_publ_idx",
                    ),
                ],
            },
        ),
    ]

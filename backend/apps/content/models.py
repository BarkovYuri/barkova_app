from django.db import models
from django.utils.text import slugify


# Транслит для генерации латинских slug'ов из кириллических заголовков.
# django.utils.text.slugify сам по себе вырезает кириллицу полностью,
# а с allow_unicode=True оставляет её как есть — обычно URL'ы хочется
# латинские. Используется в Article.save().
_RU_TO_EN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def transliterate_slug(text: str) -> str:
    return "".join(_RU_TO_EN.get(ch.lower(), ch) for ch in text)


# ============================================================================
# Глобальные простые тексты (CTA, заголовки секций, hero subtitle и т.д.)
# Используется как key/value хранилище для текстов, которые вшивались в код.
# ============================================================================


class SiteBlock(models.Model):
    """
    Простое key/value хранилище для редактируемых текстов.

    Примеры ключей:
      hero.subtitle           — подзаголовок hero (если description пустой)
      services.section_title  — заголовок секции «Как я помогаю»
      services.section_chip   — чип над заголовком секции услуг
      how_it_works.section_title
      how_it_works.section_subtitle
      faq.section_title
      faq.section_subtitle
      cta.home.title          — «Готовы начать?»
      cta.home.text           — «Запишитесь на онлайн-разбор...»
      cta.home.button         — текст кнопки
      cta.about.title
      cta.about.text
    """

    key = models.CharField("Ключ блока", max_length=100, unique=True)
    title = models.CharField(
        "Заголовок (если применимо)",
        max_length=255,
        blank=True,
    )
    content = models.TextField(
        "Содержимое",
        blank=True,
        help_text="Основной текст блока. Поддерживается простой текст и переносы строк.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Текстовый блок"
        verbose_name_plural = "Текстовые блоки"
        ordering = ["key"]

    def __str__(self):
        return self.key


# ============================================================================
# Иконки — список доступных lucide-react иконок, из которых может выбирать врач.
# Любая из этих иконок будет распознана на фронте через map.
# ============================================================================


ICON_CHOICES = [
    # Медицина и приём
    ("stethoscope", "Стетоскоп"),
    ("hospital", "Больница"),
    ("pill", "Таблетка"),
    ("syringe", "Шприц"),
    ("heart", "Сердце"),
    ("heart_pulse", "Пульс"),
    ("activity", "Активность"),
    ("microscope", "Микроскоп"),
    ("test_tube", "Пробирка"),
    # Календарь и время
    ("calendar", "Календарь"),
    ("calendar_check", "Календарь с галочкой"),
    ("calendar_days", "Календарь (дни)"),
    ("clock", "Часы"),
    # Сообщения
    ("message_square", "Сообщение"),
    ("message_circle", "Сообщение в кружке"),
    ("message_circle_heart", "Сообщение с сердечком"),
    ("send", "Отправить"),
    ("phone", "Телефон"),
    ("mail", "Почта"),
    ("users", "Люди"),
    # Документы
    ("clipboard_list", "Список (клипборд)"),
    ("file_text", "Документ"),
    ("scroll_text", "Свиток"),
    ("list_checks", "Список с галочками"),
    ("check_check", "Двойная галочка"),
    ("check_circle", "Галочка в кружке"),
    # Защита, награды
    ("shield_check", "Щит с галочкой"),
    ("award", "Награда"),
    ("badge_check", "Значок-галочка"),
    ("graduation_cap", "Шапка выпускника"),
    ("trending_up", "Растущий тренд"),
    ("sparkles", "Звёздочки"),
    # Локация и транспорт
    ("map_pin", "Метка на карте"),
    ("map", "Карта"),
    ("train", "Метро/поезд"),
    ("car", "Автомобиль"),
    ("car_taxi_front", "Такси"),
    ("building_2", "Здание"),
    # Прочее
    ("info", "Информация"),
    ("help_circle", "Вопрос"),
    ("alert_triangle", "Предупреждение"),
    ("thumbs_up", "Лайк"),
    ("smile", "Улыбка"),
]


# ============================================================================
# Услуги — секция «Как я помогаю» на главной (3 карточки)
# ============================================================================


class Service(models.Model):
    icon = models.CharField(
        "Иконка",
        max_length=40,
        choices=ICON_CHOICES,
        default="stethoscope",
    )
    title = models.CharField("Название услуги", max_length=255)
    description = models.TextField("Описание услуги")
    cta_text = models.CharField(
        "Текст кнопки/ссылки",
        max_length=100,
        default="Записаться",
    )
    cta_link = models.CharField(
        "Куда ведёт ссылка",
        max_length=255,
        default="/booking",
        help_text="Внутренняя ссылка (/booking) или полный URL.",
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
        help_text="Чем меньше — тем выше в списке.",
    )
    is_active = models.BooleanField("Показывать на сайте", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Услуга (карточка)"
        verbose_name_plural = "Услуги (карточки на главной)"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


# ============================================================================
# Шаги «Как это работает» (4 шага на главной)
# ============================================================================


class HowItWorksStep(models.Model):
    icon = models.CharField(
        "Иконка",
        max_length=40,
        choices=ICON_CHOICES,
        default="calendar_days",
    )
    title = models.CharField("Название шага", max_length=255)
    description = models.TextField("Описание шага")
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
        help_text="Шаги показываются по возрастанию этого числа.",
    )
    is_active = models.BooleanField("Показывать", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Шаг «Как это работает»"
        verbose_name_plural = "Шаги «Как это работает»"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.order + 1}. {self.title}"


# ============================================================================
# FAQ — частые вопросы
# ============================================================================


class FaqItem(models.Model):
    question = models.CharField("Вопрос", max_length=500)
    answer = models.TextField("Ответ")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Вопрос FAQ"
        verbose_name_plural = "FAQ — частые вопросы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


# ============================================================================
# «Подход к работе» — секция на /about (3 пункта)
# ============================================================================


class ApproachItem(models.Model):
    icon = models.CharField(
        "Иконка",
        max_length=40,
        choices=ICON_CHOICES,
        default="clipboard_list",
    )
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пункт «Подход к работе»"
        verbose_name_plural = "Подход к работе (страница «О враче»)"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


# ============================================================================
# Бейджи доверия — strip под hero на главной (4 пункта)
# ============================================================================


class TrustBadge(models.Model):
    icon = models.CharField(
        "Иконка",
        max_length=40,
        choices=ICON_CHOICES,
        default="shield_check",
    )
    label = models.CharField("Текст бейджа", max_length=100)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Бейдж доверия"
        verbose_name_plural = "Бейджи доверия (под hero)"
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


# ============================================================================
# Транспорт — секция «Как добраться» на /office (3+ пункта)
# ============================================================================


class TransportItem(models.Model):
    icon = models.CharField(
        "Иконка",
        max_length=40,
        choices=ICON_CHOICES,
        default="train",
    )
    title = models.CharField("Название способа", max_length=255)
    description = models.TextField("Описание")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Способ добраться"
        verbose_name_plural = "Способы добраться (страница «Очный приём»)"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


# ============================================================================
# «Что входит» — для /booking (онлайн) и /office (очный приём)
# ============================================================================


CONSULTATION_TYPE_CHOICES = [
    ("online", "Онлайн-разбор (/booking)"),
    ("office", "Очный приём (/office)"),
]


class ConsultationFeature(models.Model):
    """
    Пункт списка «Что входит» на странице записи.

    Один пункт — одна карточка/строка вроде «УЗИ органов брюшной
    полости» с иконкой и кратким описанием.
    """

    consultation_type = models.CharField(
        "Тип услуги",
        max_length=10,
        choices=CONSULTATION_TYPE_CHOICES,
        db_index=True,
    )
    icon = models.CharField(
        "Иконка",
        max_length=40,
        choices=ICON_CHOICES,
        default="check_circle",
    )
    title = models.CharField("Название пункта", max_length=255)
    description = models.TextField(
        "Описание (опционально)",
        blank=True,
        help_text="Короткое уточнение под названием. Можно оставить пустым.",
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
        help_text="Чем меньше — тем выше в списке.",
    )
    is_active = models.BooleanField("Показывать на сайте", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пункт «Что входит»"
        verbose_name_plural = "«Что входит» (booking / office)"
        ordering = ["consultation_type", "order", "id"]

    def __str__(self):
        return f"[{self.get_consultation_type_display()}] {self.title}"


# ============================================================================
# «С чем можно обратиться» — на странице /about
# ============================================================================


class ConditionCategory(models.Model):
    """Группа состояний/заболеваний, например «Печень» или «Паразитология»."""

    icon = models.CharField(
        "Иконка",
        max_length=40,
        choices=ICON_CHOICES,
        default="activity",
    )
    title = models.CharField("Название группы", max_length=255)
    description = models.TextField(
        "Подзаголовок (опционально)",
        blank=True,
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Группа «С чем можно обратиться»"
        verbose_name_plural = "«С чем можно обратиться» (страница «О враче»)"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class ConditionItem(models.Model):
    """Один пункт списка внутри группы."""

    category = models.ForeignKey(
        ConditionCategory,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Группа",
    )
    text = models.CharField("Текст пункта", max_length=500)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Пункт"
        verbose_name_plural = "Пункты"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]


# ============================================================================
# Блог / статьи
# ============================================================================


class Article(models.Model):
    """Статья блога. Длинный контент в Markdown.

    Markdown парсится на фронте через react-markdown — безопасно,
    raw HTML не рендерится.
    """

    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField(
        "URL (slug)",
        max_length=255,
        unique=True,
        blank=True,
        help_text=(
            "Латиницей через дефисы. Можно оставить пустым — "
            "сгенерируется автоматически из заголовка через транслит."
        ),
    )
    excerpt = models.CharField(
        "Краткое описание (превью)",
        max_length=500,
        blank=True,
        help_text=(
            "1-2 предложения для карточки в списке статей и для meta "
            "description в поисковой выдаче."
        ),
    )
    body = models.TextField(
        "Текст статьи (Markdown)",
        help_text=(
            "Поддерживается Markdown: ## Заголовок, **жирный**, *курсив*, "
            "[ссылка](https://...), списки, переносы строк, цитаты."
        ),
    )
    cover = models.ImageField(
        "Обложка",
        upload_to="blog/",
        blank=True,
        null=True,
    )
    cover_alt = models.CharField(
        "Alt-текст обложки (для SEO)",
        max_length=255,
        blank=True,
    )

    is_published = models.BooleanField(
        "Опубликована",
        default=False,
        help_text="Если выключено — статья не показывается на сайте.",
    )
    published_at = models.DateTimeField(
        "Дата публикации",
        null=True,
        blank=True,
        help_text=(
            "Если оставить пустым — поставится автоматически при первой "
            "публикации. Можно поставить дату вручную для backdate'инга."
        ),
    )

    meta_title = models.CharField(
        "SEO Title (опц)",
        max_length=255,
        blank=True,
        help_text="Если пусто — берётся обычный заголовок.",
    )
    meta_description = models.CharField(
        "SEO Description (опц)",
        max_length=300,
        blank=True,
        help_text="Если пусто — берётся «Краткое описание».",
    )
    keywords = models.CharField(
        "Ключевые слова (через запятую)",
        max_length=500,
        blank=True,
    )

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["is_published", "-published_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        from django.utils import timezone

        if not self.slug:
            base = slugify(transliterate_slug(self.title))[:240] or f"article-{self.pk or 'new'}"
            self.slug = base
            # Гарантируем уникальность: добавляем -2, -3, ...
            counter = 2
            while Article.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{counter}"
                counter += 1

        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)


# ============================================================================
# Юридические документы (как было)
# ============================================================================


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

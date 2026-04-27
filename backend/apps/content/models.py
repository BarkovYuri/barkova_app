from django.db import models


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
      cta.home.text           — «Запишитесь на консультацию...»
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

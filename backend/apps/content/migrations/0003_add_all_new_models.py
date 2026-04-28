"""Создаёт все новые content-модели (Service, FaqItem, HowItWorksStep,
ApproachItem, TrustBadge, TransportItem) + правит SiteBlock.

Безопасна на проде где часть таблиц уже создана через `makemigrations` внутри
контейнера в предыдущих попытках — там миграция применится через
`python manage.py migrate --fake-initial` или вручную пометится как applied.
"""
from django.db import migrations, models


ICON_CHOICES = [
    ("stethoscope", "Стетоскоп"),
    ("hospital", "Больница"),
    ("pill", "Таблетка"),
    ("syringe", "Шприц"),
    ("heart", "Сердце"),
    ("heart_pulse", "Пульс"),
    ("activity", "Активность"),
    ("microscope", "Микроскоп"),
    ("test_tube", "Пробирка"),
    ("calendar", "Календарь"),
    ("calendar_check", "Календарь с галочкой"),
    ("calendar_days", "Календарь (дни)"),
    ("clock", "Часы"),
    ("message_square", "Сообщение"),
    ("message_circle", "Сообщение в кружке"),
    ("message_circle_heart", "Сообщение с сердечком"),
    ("send", "Отправить"),
    ("phone", "Телефон"),
    ("mail", "Почта"),
    ("users", "Люди"),
    ("clipboard_list", "Список (клипборд)"),
    ("file_text", "Документ"),
    ("scroll_text", "Свиток"),
    ("list_checks", "Список с галочками"),
    ("check_check", "Двойная галочка"),
    ("check_circle", "Галочка в кружке"),
    ("shield_check", "Щит с галочкой"),
    ("award", "Награда"),
    ("badge_check", "Значок-галочка"),
    ("graduation_cap", "Шапка выпускника"),
    ("trending_up", "Растущий тренд"),
    ("sparkles", "Звёздочки"),
    ("map_pin", "Метка на карте"),
    ("map", "Карта"),
    ("train", "Метро/поезд"),
    ("car", "Автомобиль"),
    ("car_taxi_front", "Такси"),
    ("building_2", "Здание"),
    ("info", "Информация"),
    ("help_circle", "Вопрос"),
    ("alert_triangle", "Предупреждение"),
    ("thumbs_up", "Лайк"),
    ("smile", "Улыбка"),
]


class Migration(migrations.Migration):
    dependencies = [
        (
            "content",
            "0002_alter_legaldocument_options_alter_siteblock_options",
        ),
    ]

    operations = [
        # SiteBlock — изменения (verbose_name, blank, help_text)
        migrations.AlterModelOptions(
            name="siteblock",
            options={
                "ordering": ["key"],
                "verbose_name": "Текстовый блок",
                "verbose_name_plural": "Текстовые блоки",
            },
        ),
        migrations.AlterField(
            model_name="siteblock",
            name="title",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name="Заголовок (если применимо)",
            ),
        ),
        migrations.AlterField(
            model_name="siteblock",
            name="content",
            field=models.TextField(
                blank=True,
                help_text="Основной текст блока. Поддерживается простой текст и переносы строк.",
                verbose_name="Содержимое",
            ),
        ),
        # ─── Service ───
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "icon",
                    models.CharField(
                        choices=ICON_CHOICES,
                        default="stethoscope",
                        max_length=40,
                        verbose_name="Иконка",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название услуги")),
                ("description", models.TextField(verbose_name="Описание услуги")),
                (
                    "cta_text",
                    models.CharField(
                        default="Записаться",
                        max_length=100,
                        verbose_name="Текст кнопки/ссылки",
                    ),
                ),
                (
                    "cta_link",
                    models.CharField(
                        default="/booking",
                        help_text="Внутренняя ссылка (/booking) или полный URL.",
                        max_length=255,
                        verbose_name="Куда ведёт ссылка",
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Чем меньше — тем выше в списке.",
                        verbose_name="Порядок",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать на сайте")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Услуга (карточка)",
                "verbose_name_plural": "Услуги (карточки на главной)",
                "ordering": ["order", "id"],
            },
        ),
        # ─── HowItWorksStep ───
        migrations.CreateModel(
            name="HowItWorksStep",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "icon",
                    models.CharField(
                        choices=ICON_CHOICES,
                        default="calendar_days",
                        max_length=40,
                        verbose_name="Иконка",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название шага")),
                ("description", models.TextField(verbose_name="Описание шага")),
                (
                    "order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Шаги показываются по возрастанию этого числа.",
                        verbose_name="Порядок",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Шаг «Как это работает»",
                "verbose_name_plural": "Шаги «Как это работает»",
                "ordering": ["order", "id"],
            },
        ),
        # ─── FaqItem ───
        migrations.CreateModel(
            name="FaqItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("question", models.CharField(max_length=500, verbose_name="Вопрос")),
                ("answer", models.TextField(verbose_name="Ответ")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Вопрос FAQ",
                "verbose_name_plural": "FAQ — частые вопросы",
                "ordering": ["order", "id"],
            },
        ),
        # ─── ApproachItem ───
        migrations.CreateModel(
            name="ApproachItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "icon",
                    models.CharField(
                        choices=ICON_CHOICES,
                        default="clipboard_list",
                        max_length=40,
                        verbose_name="Иконка",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("description", models.TextField(verbose_name="Описание")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Пункт «Подход к работе»",
                "verbose_name_plural": "Подход к работе (страница «О враче»)",
                "ordering": ["order", "id"],
            },
        ),
        # ─── TrustBadge ───
        migrations.CreateModel(
            name="TrustBadge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "icon",
                    models.CharField(
                        choices=ICON_CHOICES,
                        default="shield_check",
                        max_length=40,
                        verbose_name="Иконка",
                    ),
                ),
                ("label", models.CharField(max_length=100, verbose_name="Текст бейджа")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Бейдж доверия",
                "verbose_name_plural": "Бейджи доверия (под hero)",
                "ordering": ["order", "id"],
            },
        ),
        # ─── TransportItem ───
        migrations.CreateModel(
            name="TransportItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "icon",
                    models.CharField(
                        choices=ICON_CHOICES,
                        default="train",
                        max_length=40,
                        verbose_name="Иконка",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название способа")),
                ("description", models.TextField(verbose_name="Описание")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Способ добраться",
                "verbose_name_plural": "Способы добраться (страница «Очный приём»)",
                "ordering": ["order", "id"],
            },
        ),
    ]

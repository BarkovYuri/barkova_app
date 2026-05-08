from django.db import migrations, models


def seed_default_data(apps, schema_editor):
    """Стартовый контент.

    «С чем можно обратиться» — точный текст, согласованный с заказчиком.
    «Что входит» — нейтральные дефолты, чтобы блок не был пустым на проде;
    врач отредактирует через админку.
    """
    ConsultationFeature = apps.get_model("content", "ConsultationFeature")
    ConditionCategory = apps.get_model("content", "ConditionCategory")
    ConditionItem = apps.get_model("content", "ConditionItem")

    online_features = [
        (
            "stethoscope",
            "Полный сбор анамнеза",
            "Подробно разбираем жалобы, историю болезни, образ жизни, "
            "хронические заболевания и принимаемые препараты.",
        ),
        (
            "file_text",
            "Разбор анализов и обследований",
            "Смотрю ваши результаты, объясняю, что они значат, и какие "
            "исследования стоит сделать дополнительно.",
        ),
        (
            "clipboard_list",
            "План лечения и наблюдения",
            "Назначения с дозировками, сроками контроля и понятными "
            "ориентирами — что и когда должно измениться.",
        ),
        (
            "send",
            "Письменное заключение",
            "После приёма получаете заключение в Telegram или VK — "
            "чтобы не запоминать на слух.",
        ),
    ]

    office_features = [
        (
            "stethoscope",
            "Очный осмотр",
            "Полный физикальный осмотр, проверка лимфоузлов, кожи, "
            "пальпация органов брюшной полости.",
        ),
        (
            "microscope",
            "УЗИ внутренних органов",
            "При необходимости проводим УЗИ прямо на приёме — "
            "печень, желчный пузырь, селезёнка, лимфоузлы.",
        ),
        (
            "test_tube",
            "Подбор лабораторных анализов",
            "Назначаю именно те анализы, которые нужны в вашей ситуации — "
            "без избыточных и шаблонных пакетов.",
        ),
        (
            "file_text",
            "Письменное заключение и план",
            "Заключение, рекомендации и схема контроля — на руки и в "
            "электронном виде.",
        ),
    ]

    for order, (icon, title, description) in enumerate(online_features):
        ConsultationFeature.objects.create(
            consultation_type="online",
            icon=icon,
            title=title,
            description=description,
            order=order,
            is_active=True,
        )

    for order, (icon, title, description) in enumerate(office_features):
        ConsultationFeature.objects.create(
            consultation_type="office",
            icon=icon,
            title=title,
            description=description,
            order=order,
            is_active=True,
        )

    conditions = [
        (
            "alert_triangle",
            "Осложнённые и длительные состояния",
            [
                "Увеличенные лимфоузлы",
                "Длительная температура, лихорадка неясного генеза",
                "Хроническая слабость и утомляемость",
                "Поствирусные состояния, постковидный синдром",
                "Непонятные кожные проявления инфекционного характера",
            ],
        ),
        (
            "activity",
            "Печень",
            [
                "Повышенные АЛТ / АСТ / ГГТ",
                "Поражения печени после вирусов и токсинов",
                "Диспансерное ведение хронических гепатитов",
                "Контроль печени по анализам и УЗИ",
            ],
        ),
        (
            "microscope",
            "Инфекционные заболевания",
            [
                "Вирусный гепатит В и С",
                "Бруцеллёз (острый / хронический)",
                "TORCH-инфекции (токсоплазмоз, ЦМВ, краснуха, герпес)",
                "Герпесвирусные инфекции (HSV-1/2, EBV, CMV, HHV-6)",
                "Лайм-боррелиоз",
                "Инфекции ЖКТ: клостридии, кампилобактер и др.",
                "Рожа (стрептококковая инфекция кожи)",
                "Инфекции, связанные со стафилококком или стрептококком",
            ],
        ),
        (
            "test_tube",
            "Паразитология",
            [
                "Лямблиоз, токсокароз, описторхоз, эхинококкоз, "
                "аскаридоз, анкилостомидоз и др.",
                "Подбор корректных анализов на паразитов",
                "Контроль лечения и схемы терапии",
            ],
        ),
        (
            "info",
            "Когда обращаться обязательно",
            [
                "Непонятные симптомы, слабость, температура",
                "Увеличенные лимфоузлы",
                "Подозрение на вирусы или паразитов",
                "Повышены ферменты печени",
                "Подготовка к беременности (TORCH)",
                "Сомнения в диагнозе или назначениях",
            ],
        ),
    ]

    for cat_order, (icon, title, items) in enumerate(conditions):
        category = ConditionCategory.objects.create(
            icon=icon,
            title=title,
            order=cat_order,
            is_active=True,
        )
        for item_order, text in enumerate(items):
            ConditionItem.objects.create(
                category=category,
                text=text,
                order=item_order,
                is_active=True,
            )


def reverse_seed(apps, schema_editor):
    """Откат стирает сидированные записи. Пользовательские правки тоже
    уйдут — поэтому даунгрейд не рекомендуется на проде."""
    apps.get_model("content", "ConsultationFeature").objects.all().delete()
    apps.get_model("content", "ConditionItem").objects.all().delete()
    apps.get_model("content", "ConditionCategory").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0003_add_all_new_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConsultationFeature",
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
                (
                    "consultation_type",
                    models.CharField(
                        choices=[
                            ("online", "Онлайн-консультация (/booking)"),
                            ("office", "Очный приём (/office)"),
                        ],
                        db_index=True,
                        max_length=10,
                        verbose_name="Тип консультации",
                    ),
                ),
                (
                    "icon",
                    models.CharField(
                        choices=[],  # выбор не валидируется на уровне БД
                        default="check_circle",
                        max_length=40,
                        verbose_name="Иконка",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название пункта")),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "Короткое уточнение под названием. Можно оставить пустым."
                        ),
                        verbose_name="Описание (опционально)",
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
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Показывать на сайте"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Пункт «Что входит»",
                "verbose_name_plural": "«Что входит» (booking / office)",
                "ordering": ["consultation_type", "order", "id"],
            },
        ),
        migrations.CreateModel(
            name="ConditionCategory",
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
                (
                    "icon",
                    models.CharField(
                        choices=[],
                        default="activity",
                        max_length=40,
                        verbose_name="Иконка",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название группы")),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        verbose_name="Подзаголовок (опционально)",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Группа «С чем можно обратиться»",
                "verbose_name_plural": "«С чем можно обратиться» (страница «О враче»)",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="ConditionItem",
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
                ("text", models.CharField(max_length=500, verbose_name="Текст пункта")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="items",
                        to="content.conditioncategory",
                        verbose_name="Группа",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пункт",
                "verbose_name_plural": "Пункты",
                "ordering": ["order", "id"],
            },
        ),
        migrations.RunPython(seed_default_data, reverse_seed),
    ]

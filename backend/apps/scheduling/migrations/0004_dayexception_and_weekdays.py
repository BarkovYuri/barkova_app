"""Добавляет модель DayException и поле weekdays (ArrayField) в AvailabilityRule."""

import django.contrib.postgres.fields
from django.db import migrations, models


WEEKDAY_CHOICES = [
    (0, "Понедельник"),
    (1, "Вторник"),
    (2, "Среда"),
    (3, "Четверг"),
    (4, "Пятница"),
    (5, "Суббота"),
    (6, "Воскресенье"),
]


class Migration(migrations.Migration):
    dependencies = [
        ("scheduling", "0003_alter_availabilityrule_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="availabilityrule",
            options={
                "ordering": ["start_date", "start_time"],
                "verbose_name": "Правило расписания",
                "verbose_name_plural": "Правила расписания",
            },
        ),
        migrations.AlterField(
            model_name="availabilityrule",
            name="weekday",
            field=models.IntegerField(
                blank=True,
                choices=WEEKDAY_CHOICES,
                help_text="Устаревшее поле. Используйте «Дни недели».",
                null=True,
                verbose_name="День недели (legacy)",
            ),
        ),
        migrations.AddField(
            model_name="availabilityrule",
            name="weekdays",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(choices=WEEKDAY_CHOICES),
                blank=True,
                default=list,
                help_text=(
                    "Выберите один или несколько дней недели, в которые "
                    "действует это правило."
                ),
                size=7,
                verbose_name="Дни недели",
            ),
        ),
        migrations.CreateModel(
            name="DayException",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("date", models.DateField(unique=True, verbose_name="Дата")),
                ("is_full_day", models.BooleanField(default=True, verbose_name="Весь день")),
                (
                    "start_time",
                    models.TimeField(
                        blank=True,
                        null=True,
                        verbose_name="Начало (если не весь день)",
                    ),
                ),
                (
                    "end_time",
                    models.TimeField(
                        blank=True,
                        null=True,
                        verbose_name="Окончание (если не весь день)",
                    ),
                ),
                (
                    "reason",
                    models.CharField(
                        blank=True,
                        help_text="Видно только в админке. На сайте слоты просто исчезают.",
                        max_length=255,
                        verbose_name="Причина / комментарий",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Выходной день / исключение",
                "verbose_name_plural": "Выходные дни / исключения",
                "ordering": ["-date"],
            },
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctors", "0009_doctorprofile_short_intro_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctorprofile",
            name="prodoktorov_rating",
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                help_text=(
                    "Например, 4.9. Показывается на главной и идёт в "
                    "structured data (звёздочки в Google)."
                ),
                max_digits=3,
                null=True,
                verbose_name="Рейтинг на ПроДокторов",
            ),
        ),
        migrations.AddField(
            model_name="doctorprofile",
            name="prodoktorov_reviews_count",
            field=models.PositiveIntegerField(
                blank=True,
                help_text=(
                    "Число отзывов с ПроДокторов. Используется вместе с "
                    "рейтингом."
                ),
                null=True,
                verbose_name="Количество отзывов на ПроДокторов",
            ),
        ),
    ]

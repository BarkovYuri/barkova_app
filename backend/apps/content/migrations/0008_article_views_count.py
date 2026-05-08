from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0007_article"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="views_count",
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    "Увеличивается автоматически при заходе на страницу. "
                    "Можно вручную сбросить или поправить, если нужно."
                ),
                verbose_name="Количество просмотров",
            ),
        ),
    ]

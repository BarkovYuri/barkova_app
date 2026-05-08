from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctors", "0008_doctorprofile_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctorprofile",
            name="short_intro",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Одно-два предложения для hero на главной странице. "
                    "Если оставить пустым — на главной будет показан "
                    "первый абзац из «Полного описания»."
                ),
                max_length=500,
                verbose_name="Короткое описание (для главной)",
            ),
        ),
        migrations.AlterField(
            model_name="doctorprofile",
            name="description",
            field=models.TextField(
                blank=True,
                help_text=(
                    "Длинный текст с абзацами. Отображается на /about. "
                    "На главной целиком НЕ показывается — для главной "
                    "используйте поле «Короткое описание» выше."
                ),
                verbose_name="Полное описание (для страницы «О враче»)",
            ),
        ),
    ]

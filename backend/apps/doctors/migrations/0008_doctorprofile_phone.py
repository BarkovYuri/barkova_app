from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctors", "0007_doctorprofile_vk_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctorprofile",
            name="phone",
            field=models.CharField(
                blank=True,
                help_text=(
                    "В международном формате, например +7 (3822) 123-45-67. "
                    "На странице «Контакты» отобразится как кликабельная "
                    "ссылка tel:."
                ),
                max_length=50,
                verbose_name="Телефон",
            ),
        ),
    ]

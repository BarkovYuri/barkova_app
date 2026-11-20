from django.db import migrations, models

# Подписи кнопок быстрых ответов в VK-боте для уже существующих вопросов.
# Применяются только к вопросам с ровно таким текстом.
BOT_LABELS = {
    "Сколько длится онлайн-разбор?": "Сколько длится разбор",
    "Как проходит онлайн-разбор?": "Как проходит разбор",
    "Что подготовить к приёму?": "Что подготовить",
    "Можно ли получить рецепт после онлайн-разбора?": "Рецепт после разбора",
}


def seed_labels(apps, schema_editor):
    FaqItem = apps.get_model("content", "FaqItem")
    for question, label in BOT_LABELS.items():
        FaqItem.objects.filter(question=question, bot_label="").update(bot_label=label)


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0012_review_credential"),
    ]

    operations = [
        migrations.AddField(
            model_name="faqitem",
            name="bot_label",
            field=models.CharField(
                blank=True,
                help_text="Короткая подпись до 40 символов. Если заполнено, вопрос появится кнопкой быстрого ответа в сообщениях сообщества VK.",
                max_length=40,
                verbose_name="Кнопка в VK-боте",
            ),
        ),
        migrations.RunPython(seed_labels, migrations.RunPython.noop),
    ]

"""
Data migration: обновляет уже засеянные тексты, упоминающие Telegram,
на формулировки, где остаётся только VK.

Правки в seed_content.py и в 0004_consultation_features_and_conditions.py
меняют только дефолты для *новых* окружений — get_or_create в seed_content
пропускает уже существующие строки. Эта миграция чинит содержимое уже
существующей (в т.ч. продовой) базы, точечно и идемпотентно: трогает
только строки, где ещё встречается старая формулировка.
"""
from django.db import migrations


REPLACEMENTS = [
    (
        "SiteBlock",
        "key",
        "faq.section_subtitle",
        "content",
        "Если ваш вопрос не нашёлся ниже — напишите в Telegram или VK, отвечу лично.",
        "Если ваш вопрос не нашёлся ниже — напишите в VK, отвечу лично.",
    ),
    (
        "HowItWorksStep",
        "title",
        "Контактные данные",
        "description",
        "Оставьте имя и телефон, опишите вопрос. Подключите Telegram или VK для уведомлений.",
        "Оставьте имя и телефон, опишите вопрос. Подключите VK для уведомлений.",
    ),
    (
        "FaqItem",
        "question",
        "Как проходит онлайн-консультация?",
        "answer",
        "Все детали приёма — формат связи, время, рекомендации — врач уточнит в Telegram или VK после подтверждения записи.",
        "Все детали приёма — формат связи, время, рекомендации — врач уточнит в VK после подтверждения записи.",
    ),
    (
        "FaqItem",
        "question",
        "Сохраняются ли мои данные в тайне?",
        "answer",
        "Да. Все ваши данные обрабатываются в соответствии с 152-ФЗ. Сообщения в Telegram и VK не пересылаются третьим лицам. Записи приёмов не ведутся — обсуждение остаётся между вами и врачом.",
        "Да. Все ваши данные обрабатываются в соответствии с 152-ФЗ. Сообщения в VK не пересылаются третьим лицам. Записи приёмов не ведутся — обсуждение остаётся между вами и врачом.",
    ),
    (
        "TrustBadge",
        "label",
        "Поддержка в Telegram / VK",
        "label",
        "Поддержка в Telegram / VK",
        "Поддержка в VK",
    ),
    (
        "ConsultationFeature",
        "title",
        "Письменное заключение",
        "description",
        "После приёма получаете заключение в Telegram или VK — чтобы не запоминать на слух.",
        "После приёма получаете заключение в VK — чтобы не запоминать на слух.",
    ),
]


def replace_telegram_mentions(apps, schema_editor):
    for model_name, lookup_field, lookup_value, text_field, old_text, new_text in REPLACEMENTS:
        model = apps.get_model("content", model_name)
        obj = model.objects.filter(**{lookup_field: lookup_value}).first()
        if not obj:
            continue
        current = getattr(obj, text_field)
        if current == old_text:
            setattr(obj, text_field, new_text)
            obj.save(update_fields=[text_field])


def restore_telegram_mentions(apps, schema_editor):
    for model_name, lookup_field, lookup_value, text_field, old_text, new_text in REPLACEMENTS:
        model = apps.get_model("content", model_name)
        # TrustBadge — lookup сам по себе меняется этой миграцией, ищем по новому значению.
        current_lookup_value = new_text if lookup_field == text_field else lookup_value
        obj = model.objects.filter(**{lookup_field: current_lookup_value}).first()
        if not obj:
            continue
        current = getattr(obj, text_field)
        if current == new_text:
            setattr(obj, text_field, old_text)
            obj.save(update_fields=[text_field])


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0009_blogcategory"),
    ]

    operations = [
        migrations.RunPython(replace_telegram_mentions, restore_telegram_mentions),
    ]

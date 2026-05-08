"""Замена «консультация» → «онлайн-разбор» в существующих SiteBlock и
FaqItem без переписывания вручную отредактированных текстов.

Применяется только к точным паттернам с учётом склонений. «Очная
консультация» отдельно — она превращается в «очный приём».
"""

from django.db import migrations


# Порядок важен: длинные/специфичные паттерны идут раньше общих.
# (kf, vt) — kept-form, value-to.
REPLACEMENTS = [
    # «Очная консультация» в любых формах → «очный приём».
    ("очная консультация", "очный приём"),
    ("Очная консультация", "Очный приём"),
    ("очной консультации", "очного приёма"),
    ("Очной консультации", "Очного приёма"),
    ("очную консультацию", "очный приём"),
    ("Очную консультацию", "Очный приём"),
    # Все формы «онлайн-консультации» → «онлайн-разбор» (на всякий случай;
    # большую часть уже обработала миграция 0005).
    ("онлайн-консультации", "онлайн-разбора"),
    ("Онлайн-консультации", "Онлайн-разборы"),
    ("онлайн-консультацию", "онлайн-разбор"),
    ("Онлайн-консультацию", "Онлайн-разбор"),
    ("онлайн-консультация", "онлайн-разбор"),
    ("Онлайн-консультация", "Онлайн-разбор"),
    # Самостоятельное слово «консультация» в разных падежах.
    # Идут после «онлайн-» и «очная», чтобы случайно не сжать.
    ("консультации", "онлайн-разбора"),
    ("консультацию", "онлайн-разбор"),
    ("консультация", "онлайн-разбор"),
    ("консультацией", "онлайн-разбором"),
    ("консультаций", "онлайн-разборов"),
]


def _replace_all(text: str) -> str:
    if not text:
        return text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def apply_changes(apps, schema_editor):
    SiteBlock = apps.get_model("content", "SiteBlock")
    FaqItem = apps.get_model("content", "FaqItem")
    Service = apps.get_model("content", "Service")
    HowItWorksStep = apps.get_model("content", "HowItWorksStep")
    ApproachItem = apps.get_model("content", "ApproachItem")
    TrustBadge = apps.get_model("content", "TrustBadge")

    for block in SiteBlock.objects.all():
        new_title = _replace_all(block.title or "")
        new_content = _replace_all(block.content or "")
        if new_title != block.title or new_content != block.content:
            block.title = new_title
            block.content = new_content
            block.save(update_fields=["title", "content", "updated_at"])

    for item in FaqItem.objects.all():
        new_q = _replace_all(item.question or "")
        new_a = _replace_all(item.answer or "")
        if new_q != item.question or new_a != item.answer:
            item.question = new_q
            item.answer = new_a
            item.save(update_fields=["question", "answer", "updated_at"])

    for service in Service.objects.all():
        new_title = _replace_all(service.title or "")
        new_desc = _replace_all(service.description or "")
        if new_title != service.title or new_desc != service.description:
            service.title = new_title
            service.description = new_desc
            service.save(update_fields=["title", "description", "updated_at"])

    for step in HowItWorksStep.objects.all():
        new_title = _replace_all(step.title or "")
        new_desc = _replace_all(step.description or "")
        if new_title != step.title or new_desc != step.description:
            step.title = new_title
            step.description = new_desc
            step.save(update_fields=["title", "description", "updated_at"])

    for approach in ApproachItem.objects.all():
        new_title = _replace_all(approach.title or "")
        new_desc = _replace_all(approach.description or "")
        if new_title != approach.title or new_desc != approach.description:
            approach.title = new_title
            approach.description = new_desc
            approach.save(update_fields=["title", "description", "updated_at"])

    for badge in TrustBadge.objects.all():
        new_label = _replace_all(badge.label or "")
        if new_label != badge.label:
            badge.label = new_label
            badge.save(update_fields=["label", "updated_at"])


def revert_changes(apps, schema_editor):
    """Безопасный no-op откат: после правок врача в админке откатывать
    в обратную сторону некорректно."""


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0005_rename_to_online_razbor"),
    ]

    operations = [
        migrations.RunPython(apply_changes, revert_changes),
    ]

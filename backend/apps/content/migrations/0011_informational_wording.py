"""
Тексты сайта под информационный формат онлайн-разбора и без устаревших
упоминаний (Telegram, Uber, Gett).

Каждая правка применяется, только если в базе стоит ровно старый текст:
если врач уже поменял его в админке, миграция ничего не трогает.
"""

from django.db import migrations

# (модель, поле, старое значение или подстрока, новое значение, режим)
# режим "exact" — поле целиком равно старому; "sub" — замена подстроки.
REPLACEMENTS = [
    (
        "Service",
        "description",
        "Быстрая запись через сайт. Выберите дату, время — и приходите на удобный вам формат.",
        "Разбор вашей ситуации по видеосвязи: анализы, симптомы, вопросы. Запись через сайт за пару минут.",
        "exact",
    ),
    (
        "HowItWorksStep",
        "description",
        "В мессенджер придёт сообщение с подтверждением записи и всеми деталями приёма.",
        "В VK придёт сообщение с подтверждением записи. Если VK нет, врач позвонит.",
        "exact",
    ),
    (
        "HowItWorksStep",
        "description",
        "В назначенное время — выходите на связь. Получаете план обследований и рекомендации.",
        "В назначенное время выходите на связь. После разбора получаете памятку с главным по вашей теме.",
        "exact",
    ),
    (
        "FaqItem",
        "answer",
        "Базовый приём — 60 минут. Этого достаточно, чтобы разобрать жалобы, обсудить уже имеющиеся анализы и составить план.",
        "Около 60 минут. Этого достаточно, чтобы разобрать ваш вопрос и уже имеющиеся анализы.",
        "exact",
    ),
    ("FaqItem", "answer", "в Telegram или VK", "в VK или по телефону", "sub"),
    ("FaqItem", "answer", "Сообщения в Telegram и VK", "Сообщения в VK", "sub"),
    (
        "TransportItem",
        "description",
        "Яндекс.Такси, Uber или Gett — удобно и быстро",
        "Яндекс Go или любое другое такси",
        "exact",
    ),
    ("SiteBlock", "content", "Мессенджеры", "Соцсети и почта", "exact"),
    (
        "SiteBlock",
        "content",
        "Запишитесь на онлайн-разбор уже сегодня и получите профессиональную помощь",
        "Запишитесь на онлайн-разбор и спокойно разберитесь в своей ситуации вместе с врачом",
        "exact",
    ),
]

PROFILE_REPLACEMENTS = [
    ("объясняю простым языком, лечу без паники.", "объясняю простым языком и помогаю без паники."),
]


def forwards(apps, schema_editor):
    for model_name, field, old, new, mode in REPLACEMENTS:
        model = apps.get_model("content", model_name)
        if mode == "exact":
            model.objects.filter(**{field: old}).update(**{field: new})
            continue
        for obj in model.objects.filter(**{f"{field}__contains": old}):
            setattr(obj, field, getattr(obj, field).replace(old, new))
            obj.save(update_fields=[field])

    Service = apps.get_model("content", "Service")
    # «Рекомендации» — не услуга: обещание «назначений» спорит с
    # информационным форматом. Скрываем, а не удаляем: можно вернуть в админке.
    Service.objects.filter(title="Рекомендации").update(is_active=False)
    # Карточка «Очный приём» вела на онлайн-запись.
    Service.objects.filter(title="Очный приём", cta_link__in=["", "/booking"]).update(
        cta_link="/office", cta_text="Подробнее"
    )

    DoctorProfile = apps.get_model("doctors", "DoctorProfile")
    for profile in DoctorProfile.objects.all():
        intro = profile.short_intro or ""
        for old, new in PROFILE_REPLACEMENTS:
            intro = intro.replace(old, new)
        if intro != (profile.short_intro or ""):
            profile.short_intro = intro
            profile.save(update_fields=["short_intro"])


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0010_remove_telegram_mentions_from_content"),
        ("doctors", "0010_prodoktorov_rating"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]

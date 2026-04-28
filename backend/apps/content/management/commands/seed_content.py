"""
Засеять контент сайта значениями по умолчанию.

Используется один раз после первого деплоя новых моделей,
чтобы фронт сразу получил рабочий контент, идентичный тому,
что был раньше захардкожен в JSX.

Запуск:
    python manage.py seed_content

Команда идемпотентна: повторный запуск не дублирует данные.
Чтобы перезалить заново — добавьте флаг --reset:
    python manage.py seed_content --reset
"""

from django.core.management.base import BaseCommand

from apps.content.models import (
    ApproachItem,
    FaqItem,
    HowItWorksStep,
    Service,
    SiteBlock,
    TransportItem,
    TrustBadge,
)


SITE_BLOCKS = [
    {
        "key": "hero.subtitle",
        "title": "Подзаголовок hero",
        "content": (
            "Помогаю взрослым и детям с инфекционными заболеваниями: "
            "от диагностики до длительного сопровождения."
        ),
    },
    {
        "key": "hero.specialty_chip",
        "title": "Чип над именем (главная)",
        "content": "Врач-инфекционист",
    },
    {
        "key": "services.section_chip",
        "title": "Чип секции услуг",
        "content": "Услуги",
    },
    {
        "key": "services.section_title",
        "title": "Заголовок секции услуг",
        "content": "Как я помогаю",
    },
    {
        "key": "how_it_works.section_chip",
        "title": "Чип секции «Как это работает»",
        "content": "Процесс",
    },
    {
        "key": "how_it_works.section_title",
        "title": "Заголовок секции «Как это работает»",
        "content": "Как это работает",
    },
    {
        "key": "how_it_works.section_subtitle",
        "title": "Подзаголовок секции «Как это работает»",
        "content": (
            "От первой записи до получения рекомендаций — всё прозрачно "
            "и предсказуемо"
        ),
    },
    {
        "key": "faq.section_chip",
        "title": "Чип секции FAQ",
        "content": "Частые вопросы",
    },
    {
        "key": "faq.section_title",
        "title": "Заголовок секции FAQ",
        "content": "Что обычно спрашивают",
    },
    {
        "key": "faq.section_subtitle",
        "title": "Подзаголовок секции FAQ",
        "content": (
            "Если ваш вопрос не нашёлся ниже — напишите в Telegram или VK, "
            "отвечу лично."
        ),
    },
    {
        "key": "cta.home.title",
        "title": "Заголовок CTA на главной",
        "content": "Готовы начать?",
    },
    {
        "key": "cta.home.text",
        "title": "Текст CTA на главной",
        "content": (
            "Запишитесь на консультацию уже сегодня и получите "
            "профессиональную помощь"
        ),
    },
    {
        "key": "cta.home.button",
        "title": "Кнопка CTA на главной",
        "content": "Записаться сейчас",
    },
    {
        "key": "cta.about.title",
        "title": "Заголовок CTA на /about",
        "content": "Готовы получить помощь?",
    },
    {
        "key": "cta.about.text",
        "title": "Текст CTA на /about",
        "content": "Запишитесь на консультацию и начните путь к выздоровлению",
    },
    {
        "key": "approach.section_chip",
        "title": "Чип секции «Подход к работе»",
        "content": "Подход к работе",
    },
    {
        "key": "approach.section_title",
        "title": "Заголовок секции «Подход к работе»",
        "content": "Спокойно, понятно и по делу",
    },
    # ──────────── /booking ────────────
    {
        "key": "booking.section_chip",
        "title": "Чип на странице записи",
        "content": "Онлайн-консультация",
    },
    {
        "key": "booking.section_title",
        "title": "Заголовок страницы записи",
        "content": "Запись на онлайн-консультацию",
    },
    {
        "key": "booking.section_subtitle",
        "title": "Подзаголовок страницы записи",
        "content": (
            "Выберите удобную дату и время, затем оставьте свои данные для "
            "онлайн-консультации."
        ),
    },
    # ──────────── /office ────────────
    {
        "key": "office.section_chip",
        "title": "Чип на странице очного приёма",
        "content": "Очный приём",
    },
    {
        "key": "office.section_title",
        "title": "Заголовок очного приёма",
        "content": "Запись на очную консультацию",
    },
    {
        "key": "office.section_subtitle",
        "title": "Подзаголовок очного приёма",
        "content": (
            "Запись на очный приём осуществляется через платформу ПроДокторов"
        ),
    },
    {
        "key": "office.location.title",
        "title": "Заголовок блока «Местоположение»",
        "content": "Местоположение",
    },
    {
        "key": "office.location.subtitle",
        "title": "Подзаголовок блока «Местоположение»",
        "content": "На карте показана точка, где проходит очная консультация",
    },
    {
        "key": "office.directions.title",
        "title": "Заголовок «Как добраться»",
        "content": "Как добраться?",
    },
    {
        "key": "office.cta.text",
        "title": "Текст CTA на /office",
        "content": "Готовы записаться на очный приём?",
    },
    {
        "key": "office.cta.button_prodoktorov",
        "title": "Кнопка «Через ПроДокторов»",
        "content": "Запишитесь через ПроДокторов",
    },
    {
        "key": "office.cta.button_online",
        "title": "Кнопка «Онлайн-консультация»",
        "content": "Записаться на онлайн-консультацию",
    },
    # ──────────── /contacts ────────────
    {
        "key": "contacts.section_title",
        "title": "Заголовок страницы контактов",
        "content": "Контакты",
    },
    {
        "key": "contacts.section_subtitle",
        "title": "Подзаголовок страницы контактов",
        "content": "Свяжитесь со мной удобным для вас способом",
    },
    {
        "key": "contacts.social.title",
        "title": "Заголовок блока «Мессенджеры»",
        "content": "Мессенджеры",
    },
    {
        "key": "contacts.map.title",
        "title": "Заголовок карты на /contacts",
        "content": "Где проходит приём",
    },
    {
        "key": "contacts.cta.text",
        "title": "Текст CTA на /contacts",
        "content": "Выберите удобный для вас способ связи или запишитесь сразу:",
    },
    {
        "key": "contacts.cta.button",
        "title": "Кнопка CTA на /contacts",
        "content": "Записаться на консультацию",
    },
]


SERVICES = [
    {
        "icon": "clipboard_list",
        "title": "Онлайн-консультация",
        "description": (
            "Быстрая запись через сайт. Выберите дату, время — "
            "и приходите на удобный вам формат."
        ),
        "cta_text": "Записаться",
        "cta_link": "/booking",
        "order": 0,
    },
    {
        "icon": "hospital",
        "title": "Очный приём",
        "description": (
            "Личный приём в кабинете. Полная диагностика и индивидуально "
            "подобранное лечение."
        ),
        "cta_text": "Записаться",
        "cta_link": "/booking",
        "order": 1,
    },
    {
        "icon": "pill",
        "title": "Рекомендации",
        "description": (
            "Профессиональные советы и назначения, основанные на актуальных "
            "клинических протоколах."
        ),
        "cta_text": "Записаться",
        "cta_link": "/booking",
        "order": 2,
    },
]


HOW_IT_WORKS = [
    {
        "icon": "calendar_days",
        "title": "Выбор даты",
        "description": (
            "Откройте календарь и выберите удобный день и время. "
            "Все свободные слоты подсвечены."
        ),
        "order": 0,
    },
    {
        "icon": "message_square",
        "title": "Контактные данные",
        "description": (
            "Оставьте имя и телефон, опишите вопрос. Подключите Telegram "
            "или VK для уведомлений."
        ),
        "order": 1,
    },
    {
        "icon": "check_check",
        "title": "Подтверждение",
        "description": (
            "В мессенджер придёт сообщение с подтверждением записи и всеми "
            "деталями приёма."
        ),
        "order": 2,
    },
    {
        "icon": "stethoscope",
        "title": "Приём",
        "description": (
            "В назначенное время — выходите на связь. Получаете план "
            "обследований и рекомендации."
        ),
        "order": 3,
    },
]


FAQ = [
    {
        "question": "Сколько длится онлайн-консультация?",
        "answer": (
            "Базовый приём — 30 минут. Этого достаточно, чтобы разобрать "
            "жалобы, обсудить уже имеющиеся анализы и составить план. "
            "Если случай сложный — возможно продление."
        ),
        "order": 0,
    },
    {
        "question": "Как проходит онлайн-консультация?",
        "answer": (
            "Все детали приёма — формат связи, время, рекомендации — "
            "врач уточнит в Telegram или VK после подтверждения записи."
        ),
        "order": 1,
    },
    {
        "question": "Что подготовить к приёму?",
        "answer": (
            "Свежие анализы (если есть), список текущих лекарств с "
            "дозировками, краткую хронологию симптомов: когда началось, "
            "что меняли, что помогало. Документы можно прикрепить к "
            "заявке заранее."
        ),
        "order": 2,
    },
    {
        "question": "Можно ли получить рецепт после онлайн-приёма?",
        "answer": (
            "После онлайн-консультации врач может оформить рекомендации и "
            "направления. Рецепт на рецептурные препараты по правилам РФ "
            "выдаётся на очном приёме либо через подключённую электронную "
            "систему, если она доступна в вашем регионе."
        ),
        "order": 3,
    },
    {
        "question": "Сохраняются ли мои данные в тайне?",
        "answer": (
            "Да. Все ваши данные обрабатываются в соответствии с 152-ФЗ. "
            "Сообщения в Telegram и VK не пересылаются третьим лицам. "
            "Записи приёмов не ведутся — обсуждение остаётся между вами "
            "и врачом."
        ),
        "order": 4,
    },
    {
        "question": "Что делать, если стало хуже после консультации?",
        "answer": (
            "Если состояние ухудшилось — напишите в тот же мессенджер, где "
            "подтверждали запись. Доктор постарается ответить максимально "
            "быстро. При неотложной ситуации звоните в скорую помощь "
            "(103 или 112)."
        ),
        "order": 5,
    },
]


APPROACH = [
    {
        "icon": "clipboard_list",
        "title": "Разбор жалоб",
        "description": (
            "Детальный анализ симптомов, анализов и уже проведённых "
            "обследований"
        ),
        "order": 0,
    },
    {
        "icon": "list_checks",
        "title": "Структурированный план",
        "description": (
            "Пациент получает ясный план: что делать, что наблюдать, "
            "какие обследования нужны"
        ),
        "order": 1,
    },
    {
        "icon": "check_circle",
        "title": "Удобный формат",
        "description": (
            "Онлайн-консультация через сайт или очный приём через "
            "ПроДокторов"
        ),
        "order": 2,
    },
]


TRANSPORT = [
    {
        "icon": "train",
        "title": "На метро",
        "description": "Ближайшая станция метро в 5 минутах пешком от кабинета",
        "order": 0,
    },
    {
        "icon": "car",
        "title": "На автомобиле",
        "description": "Рядом с кабинетом есть парковка для пациентов",
        "order": 1,
    },
    {
        "icon": "car_taxi_front",
        "title": "На такси",
        "description": "Яндекс.Такси, Uber или Gett — удобно и быстро",
        "order": 2,
    },
]


TRUST_BADGES = [
    {"icon": "shield_check", "label": "Безопасность данных", "order": 0},
    {"icon": "award", "label": "Подтверждённый стаж", "order": 1},
    {
        "icon": "message_circle_heart",
        "label": "Поддержка в Telegram / VK",
        "order": 2,
    },
    {"icon": "calendar_check", "label": "Запись 24/7", "order": 3},
]


class Command(BaseCommand):
    help = "Засеять контент сайта значениями по умолчанию."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Удалить существующие записи и засеять заново.",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        groups = [
            (SiteBlock, "key", SITE_BLOCKS, "текстовый блок"),
            (Service, "title", SERVICES, "услуга"),
            (HowItWorksStep, "title", HOW_IT_WORKS, "шаг"),
            (FaqItem, "question", FAQ, "вопрос FAQ"),
            (ApproachItem, "title", APPROACH, "пункт подхода"),
            (TransportItem, "title", TRANSPORT, "способ добраться"),
            (TrustBadge, "label", TRUST_BADGES, "бейдж доверия"),
        ]

        for model, unique_field, items, label in groups:
            if reset:
                deleted, _ = model.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(
                        f"  Удалено {deleted} {label}(-ей) (--reset)"
                    )
                )

            created = 0
            skipped = 0
            for item in items:
                lookup = {unique_field: item[unique_field]}
                obj, was_created = model.objects.get_or_create(
                    **lookup, defaults=item
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  {label}: создано {created}, пропущено {skipped}"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nГотово."))

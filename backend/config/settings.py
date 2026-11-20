from pathlib import Path
import os

from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Add it to your .env file or environment."
    )
SECRET_KEY = _secret_key

DEBUG = os.getenv("DEBUG", "False") == "True"

_DEFAULT_ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "backend",
    "nginx",
    "doctor-barkova.ru",
    "www.doctor-barkova.ru",
]

_extra_hosts = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS_EXTRA", "").split(",")
    if h.strip()
]
ALLOWED_HOSTS = _DEFAULT_ALLOWED_HOSTS + _extra_hosts

_DEFAULT_CSRF_TRUSTED_ORIGINS = [
    "https://doctor-barkova.ru",
    "https://www.doctor-barkova.ru",
]
_extra_csrf = [
    o.strip()
    for o in os.getenv("CSRF_TRUSTED_ORIGINS_EXTRA", "").split(",")
    if o.strip()
]
CSRF_TRUSTED_ORIGINS = _DEFAULT_CSRF_TRUSTED_ORIGINS + _extra_csrf

INSTALLED_APPS = [
    # Unfold должен быть ПЕРЕД django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",  # для ArrayField в scheduling.AvailabilityRule

    "rest_framework",
    "corsheaders",

    "apps.core",
    "apps.doctors",
    "apps.content",
    "apps.scheduling",
    "apps.appointments",
    "apps.integrations",
    "apps.notifications.apps.NotificationsConfig",
]


# ============================================================================
# Django Unfold — настройка визуала админки
# ============================================================================

UNFOLD = {
    "SITE_TITLE": "Кабинет врача",
    "SITE_HEADER": "Кабинет врача",
    "SITE_SUBHEADER": "Управление сайтом и записями",
    "SITE_URL": "/",
    "SITE_DROPDOWN": [
        {
            "icon": "language",
            "title": "На сайт",
            "link": "/",
        },
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": None,
    "DASHBOARD_CALLBACK": None,
    "LOGIN": {
        "image": None,
        "redirect_after": lambda request: "/admin/",
    },
    "STYLES": [],
    "SCRIPTS": [],
    "BORDER_RADIUS": "8px",
    "COLORS": {
        "primary": {
            "50": "240 250 251",
            "100": "216 241 243",
            "200": "179 227 232",
            "300": "132 205 213",
            "400": "76 177 189",
            "500": "47 149 163",
            "600": "14 116 144",
            "700": "21 94 117",
            "800": "22 78 99",
            "900": "13 58 72",
            "950": "8 42 53",
        },
    },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Главное",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Профиль врача",
                        "icon": "badge",
                        "link": "/admin/doctors/doctorprofile/",
                    },
                    {
                        "title": "Записи пациентов",
                        "icon": "event_note",
                        "link": "/admin/appointments/appointment/",
                    },
                ],
            },
            {
                "title": "Расписание приёма",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Слоты времени",
                        "icon": "schedule",
                        "link": "/admin/scheduling/timeslot/",
                    },
                    {
                        "title": "Правила расписания",
                        "icon": "calendar_month",
                        "link": "/admin/scheduling/availabilityrule/",
                    },
                    {
                        "title": "Выходные дни",
                        "icon": "event_busy",
                        "link": "/admin/scheduling/dayexception/",
                    },
                ],
            },
            {
                "title": "Главная страница сайта",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Бейджи доверия (под фото)",
                        "icon": "verified",
                        "link": "/admin/content/trustbadge/",
                    },
                    {
                        "title": "Услуги «Как я помогаю»",
                        "icon": "medical_services",
                        "link": "/admin/content/service/",
                    },
                    {
                        "title": "Шаги «Как это работает»",
                        "icon": "format_list_numbered",
                        "link": "/admin/content/howitworksstep/",
                    },
                    {
                        "title": "Вопросы FAQ",
                        "icon": "help_outline",
                        "link": "/admin/content/faqitem/",
                    },
                ],
            },
            {
                "title": "Страница «О враче»",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Подход к работе",
                        "icon": "psychology",
                        "link": "/admin/content/approachitem/",
                    },
                    {
                        "title": "С чем можно обратиться",
                        "icon": "checklist",
                        "link": "/admin/content/conditioncategory/",
                    },
                ],
            },
            {
                "title": "Страница «Запись» / «Очный приём»",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "«Что входит» (booking + office)",
                        "icon": "fact_check",
                        "link": "/admin/content/consultationfeature/",
                    },
                ],
            },
            {
                "title": "Блог",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Статьи",
                        "icon": "article",
                        "link": "/admin/content/article/",
                    },
                    {
                        "title": "Кластеры (категории)",
                        "icon": "folder",
                        "link": "/admin/content/blogcategory/",
                    },
                ],
            },
            {
                "title": "Страница «Очный приём»",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Способы добраться",
                        "icon": "directions",
                        "link": "/admin/content/transportitem/",
                    },
                ],
            },
            {
                "title": "Тексты сайта",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Заголовки и тексты",
                        "icon": "text_snippet",
                        "link": "/admin/content/siteblock/",
                    },
                    {
                        "title": "Юридические документы",
                        "icon": "gavel",
                        "link": "/admin/content/legaldocument/",
                    },
                ],
            },
            {
                "title": "Система",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Пользователи",
                        "icon": "person",
                        "link": "/admin/auth/user/",
                    },
                    {
                        "title": "Группы",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                    {
                        "title": "Логи уведомлений",
                        "icon": "notifications",
                        "link": "/admin/doctor_notifications/notificationlog/",
                    },
                    {
                        "title": "Диалоги VK",
                        "icon": "forum",
                        "link": "/admin/doctor_notifications/vkdialogstate/",
                    },
                ],
            },
        ],
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "doctor_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
# Часовой пояс, в котором врач вводит слоты расписания. Слоты хранятся как
# «дата + время» без пояса, поэтому от этой настройки зависят напоминания,
# закрытие записи за час до начала и подпись времени на сайте.
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Tomsk")

USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
LOGIN_URL = "/admin/login/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://doctor-barkova.ru",
    "https://www.doctor-barkova.ru",
]

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        *(["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    ],
    # Перед Django стоит ровно один прокси (nginx), который дописывает
    # реальный IP клиента в конец X-Forwarded-For. Без этой настройки DRF
    # брал весь заголовок целиком, и лимиты обходились подделкой заголовка.
    "NUM_PROXIES": 1,
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # Глобальный AnonRateThrottle намеренно не подключаем: frontend
    # делает SSR-запросы к /api/* с одного IP докер-контейнера, и общий
    # лимит 200/hour сжигается за минуту, ломая весь сайт. Точечные
    # лимиты на критичные endpoint'ы (создание записи, prelink) остаются —
    # они подключены через throttle_classes/throttle_scope в нужных views
    # (см. apps/core/throttling.py).
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "appointment_create": "10/hour",
        "slot_reserve": "60/hour",
        "vk_status": "300/hour",
        "article_view": "120/hour",
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

LOG_FORMAT = os.getenv("LOG_FORMAT", "json" if not DEBUG else "verbose").lower()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

_json_formatter: dict[str, str] = {
    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
}
try:
    import pythonjsonlogger.jsonlogger  # noqa: F401

    _json_formatter["()"] = "pythonjsonlogger.jsonlogger.JsonFormatter"
except ImportError:
    _json_formatter["()"] = "logging.Formatter"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "json": _json_formatter,
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": LOG_FORMAT if LOG_FORMAT in ("json", "verbose") else "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# ============================================================================
# SENTRY (optional — only enabled when SENTRY_DSN is set)
# ============================================================================

SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip()
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.redis import RedisIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
                CeleryIntegration(),
                RedisIntegration(),
                LoggingIntegration(level=None, event_level=None),
            ],
            environment=os.getenv("SENTRY_ENVIRONMENT", "production" if not DEBUG else "development"),
            release=os.getenv("SENTRY_RELEASE") or None,
            send_default_pii=False,
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0")),
        )
    except ImportError:
        import warnings

        warnings.warn(
            "SENTRY_DSN is set but sentry-sdk is not installed. "
            "Add `sentry-sdk` to requirements.txt to enable error reporting.",
            RuntimeWarning,
        )

# ============================================================================
# VK: сообщество, VK ID, бот и оповещения врача
# ============================================================================
#
# Telegram в проекте не используется вообще: и пациентам, и врачу всё
# приходит через сообщения сообщества ВКонтакте.

def _env_list(name: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN", "")
VK_GROUP_ID = os.getenv("VK_GROUP_ID", "")
# Короткое имя сообщества (vk.com/<domain>). Нужно для ссылки vk.me/<domain>,
# которая на телефоне сразу открывает диалог в приложении VK.
VK_GROUP_DOMAIN = os.getenv("VK_GROUP_DOMAIN", "")
VK_CALLBACK_CONFIRMATION_CODE = os.getenv("VK_CALLBACK_CONFIRMATION_CODE", "")
VK_CALLBACK_SECRET = os.getenv("VK_CALLBACK_SECRET", "")
VK_APP_ID = os.getenv("VK_APP_ID", "")
VK_API_VERSION = os.getenv("VK_API_VERSION", "5.199")
VK_API_TIMEOUT = int(os.getenv("VK_API_TIMEOUT", "15"))

# Личные VK-аккаунты врача/администратора, которым сообщество шлёт алерты:
# новая запись, отмена, входящее сообщение пациента, утренняя сводка.
# Каждый получатель должен один раз написать сообществу, иначе VK не даст
# сообществу писать ему первым.
VK_DOCTOR_USER_IDS = _env_list("VK_DOCTOR_USER_IDS")

# Резервный канал: если VK-алерт врачу не ушёл, дублируем на email.
DOCTOR_ALERT_EMAILS = _env_list("DOCTOR_ALERT_EMAILS")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True") == "True"
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False") == "True"
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "noreply@doctor-barkova.ru")
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)

# Поведение бота в диалоге сообщества.
# Приветствие с кнопкой записи — не чаще раза в N дней на человека.
VK_BOT_GREETING_COOLDOWN_DAYS = int(os.getenv("VK_BOT_GREETING_COOLDOWN_DAYS", "30"))
# После ручного ответа врача бот молчит в этом диалоге N часов.
VK_BOT_OPERATOR_PAUSE_HOURS = int(os.getenv("VK_BOT_OPERATOR_PAUSE_HOURS", "24"))
# Алерт врачу о входящих сообщениях — не чаще раза в N минут на собеседника.
VK_DOCTOR_ALERT_COOLDOWN_MINUTES = int(os.getenv("VK_DOCTOR_ALERT_COOLDOWN_MINUTES", "30"))

# Публичный базовый URL сайта — для ссылок в уведомлениях и клавиатурах.
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://doctor-barkova.ru").rstrip("/")

# Город, по времени которого ведётся расписание (в родительном падеже).
# Используется в подписи «время указано по времени Томска (МСК+4)».
SCHEDULE_CITY_GENITIVE = os.getenv("SCHEDULE_CITY_GENITIVE", "Томска")

# Ограничения на файлы, которые пациент прикладывает к записи.
APPOINTMENT_MAX_FILES = int(os.getenv("APPOINTMENT_MAX_FILES", "5"))
APPOINTMENT_MAX_FILE_MB = int(os.getenv("APPOINTMENT_MAX_FILE_MB", "10"))

if VK_GROUP_TOKEN and not VK_GROUP_ID:
    import warnings

    warnings.warn("VK_GROUP_TOKEN задан, а VK_GROUP_ID нет: VK-уведомления работать не будут.", RuntimeWarning, stacklevel=1)


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

# Shared cache backend. Без него django.core.cache по умолчанию локален
# (locmem) на каждый gunicorn-воркер — инвалидация кэша срабатывает только
# в одном процессе, остальные продолжают отдавать stale данные.
_REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL", "redis://redis:6379/2")
CACHES = {
    "default": (
        # Для локальной разработки без Redis: REDIS_CACHE_URL=locmem://
        {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "dev"}
        if _REDIS_CACHE_URL.startswith("locmem://")
        else {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _REDIS_CACHE_URL,
            "TIMEOUT": 300,
            "KEY_PREFIX": "doctor_app",
        }
    ),
}
# Для локальной разработки без брокера: задачи выполняются сразу в процессе.
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "False") == "True"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 10
CELERY_TASK_SOFT_TIME_LIMIT = 60 * 8

CELERY_BEAT_SCHEDULE = {
    "deactivate-near-slots-every-5-minutes": {
        "task": "apps.scheduling.tasks.deactivate_near_slots",
        "schedule": 300.0,
    },
    "send-appointment-reminders-every-minute": {
        "task": "apps.appointments.tasks.send_appointment_reminders",
        "schedule": 60.0,
    },
    "doctor-daily-digest": {
        "task": "apps.notifications.tasks.send_doctor_daily_digest",
        "schedule": crontab(hour=int(os.getenv("DOCTOR_DIGEST_HOUR", "8")), minute=0),
    },
}
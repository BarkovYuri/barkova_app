from pathlib import Path
import os
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

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "backend",
    "nginx",
    "doctor-barkova.ru",
    "www.doctor-barkova.ru",
    "5.42.126.206",
]

CSRF_TRUSTED_ORIGINS = [
    "https://doctor-barkova.ru",
    "https://www.doctor-barkova.ru",
]

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

    "rest_framework",
    "corsheaders",

    "apps.core",
    "apps.doctors",
    "apps.content",
    "apps.scheduling",
    "apps.appointments",
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
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Записи и расписание",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Записи пациентов",
                        "icon": "event_note",
                        "link": "/admin/appointments/appointment/",
                    },
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
                "title": "Контент сайта",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Профиль врача",
                        "icon": "badge",
                        "link": "/admin/doctors/doctorprofile/",
                    },
                    {
                        "title": "Услуги (главная)",
                        "icon": "medical_services",
                        "link": "/admin/content/service/",
                    },
                    {
                        "title": "Шаги «Как это работает»",
                        "icon": "format_list_numbered",
                        "link": "/admin/content/howitworksstep/",
                    },
                    {
                        "title": "FAQ",
                        "icon": "help_outline",
                        "link": "/admin/content/faqitem/",
                    },
                    {
                        "title": "Подход к работе",
                        "icon": "psychology",
                        "link": "/admin/content/approachitem/",
                    },
                    {
                        "title": "Бейджи доверия",
                        "icon": "verified",
                        "link": "/admin/content/trustbadge/",
                    },
                    {
                        "title": "Текстовые блоки",
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

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"

USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://doctor-barkova.ru",
    "https://www.doctor-barkova.ru",
]

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "200/hour",
        "appointment_create": "10/hour",
        "prelink": "30/hour",
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter" if False else "logging.Formatter",  # Fallback format
            "format": "[%(asctime)s] %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "telegram_bot": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "vk_bot": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ============================================================================
# BOT CONFIGURATION
# ============================================================================

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")

# VK (VKontakte) Bot Settings
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN", "")
VK_GROUP_ID = os.getenv("VK_GROUP_ID", "")
VK_GROUP_DOMAIN = os.getenv("VK_GROUP_DOMAIN", "")
VK_CALLBACK_CONFIRMATION_CODE = os.getenv("VK_CALLBACK_CONFIRMATION_CODE", "")
VK_APP_ID = os.getenv("VK_APP_ID", "")
VK_APP_SECRET = os.getenv("VK_APP_SECRET", "")
VK_ID_REDIRECT_URL = os.getenv(
    "VK_ID_REDIRECT_URL",
    "https://doctor-barkova.ru/auth/vk/callback",
)
VK_CALLBACK_SECRET = os.getenv("VK_CALLBACK_SECRET", "")

# Bot API Settings
VK_API_VERSION = os.getenv("VK_API_VERSION", "5.199")
API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "30"))
BOT_POLLING_TIMEOUT = int(os.getenv("BOT_POLLING_TIMEOUT", "25"))

# Booking Link
BOOKING_LINK = os.getenv("BOOKING_LINK", "https://doctor-barkova.ru/booking")

# Публичный базовый URL сайта — используется для ссылок в уведомлениях/клавиатурах
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://doctor-barkova.ru")

# Token Configuration
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_bot_configuration() -> None:
    """
    Validate bot configuration at startup.
    
    Ensures all required environment variables are set and valid.
    
    Raises:
        ImproperlyConfigured: If required settings are missing or invalid
    """
    from django.core.exceptions import ImproperlyConfigured
    
    # Validate Telegram settings (optional but warn if partially configured)
    if TELEGRAM_BOT_TOKEN and not TELEGRAM_BOT_USERNAME:
        import warnings
        warnings.warn(
            "TELEGRAM_BOT_TOKEN is set but TELEGRAM_BOT_USERNAME is not. "
            "Telegram notifications will not work properly.",
            RuntimeWarning
        )
    
    # Validate VK settings (optional but warn if partially configured)
    if VK_GROUP_TOKEN and not VK_GROUP_ID:
        import warnings
        warnings.warn(
            "VK_GROUP_TOKEN is set but VK_GROUP_ID is not. "
            "VK notifications will not work properly.",
            RuntimeWarning
        )
    
    # Validate timeout settings
    if API_REQUEST_TIMEOUT <= 0:
        raise ImproperlyConfigured("API_REQUEST_TIMEOUT must be > 0")
    
    if BOT_POLLING_TIMEOUT <= 0:
        raise ImproperlyConfigured("BOT_POLLING_TIMEOUT must be > 0")
    
    if TOKEN_EXPIRY_HOURS <= 0:
        raise ImproperlyConfigured("TOKEN_EXPIRY_HOURS must be > 0")


# Call validation only if not in migrations
if os.getenv("DJANGO_SETTINGS_MODULE", "").endswith("settings"):
    try:
        validate_bot_configuration()
    except Exception as exc:
        import warnings
        warnings.warn(f"Bot configuration validation warning: {exc}", RuntimeWarning)


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
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
}
"""
Один раз настраивает Telegram-бота:
  • setMyCommands  — список команд (синяя кнопка «Menu» слева)
  • setChatMenuButton — Web App кнопка снизу слева (открывает Mini App)

Использование:
    python manage.py setup_telegram_bot

Идемпотентно — можно запускать после каждого деплоя.
"""

import json
from urllib import error, parse, request

from django.conf import settings
from django.core.management.base import BaseCommand


COMMANDS = [
    {"command": "start", "description": "Главное меню бота"},
    {"command": "book", "description": "Записаться на консультацию"},
    {"command": "myappointments", "description": "Мои записи"},
    {"command": "help", "description": "Справка"},
]


def _api_url(method: str) -> str:
    return f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"


def _post(method: str, payload: dict) -> dict:
    body = parse.urlencode(
        {k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
         for k, v in payload.items()}
    ).encode("utf-8")
    req = request.Request(_api_url(method), data=body, method="POST")
    try:
        with request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore")
        return {"ok": False, "error": f"HTTP {exc.code}: {body_text}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


class Command(BaseCommand):
    help = "Настроить Telegram-бота: команды и Menu Button (Web App)."

    def handle(self, *args, **options):
        if not getattr(settings, "TELEGRAM_BOT_TOKEN", ""):
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN не задан в env"))
            return

        site_url = getattr(settings, "PUBLIC_BASE_URL", "https://doctor-barkova.ru")
        web_app_url = f"{site_url}/booking?tg=1"

        # 1. Команды
        self.stdout.write("Регистрирую команды...")
        result = _post("setMyCommands", {"commands": COMMANDS})
        if result.get("ok"):
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {len(COMMANDS)} команд зарегистрировано"
                )
            )
        else:
            self.stderr.write(
                self.style.ERROR(f"  ✗ Ошибка: {result.get('error') or result}")
            )

        # 2. Menu Button с Web App
        self.stdout.write("Устанавливаю Menu Button (Web App)...")
        result = _post(
            "setChatMenuButton",
            {
                "menu_button": {
                    "type": "web_app",
                    "text": "Записаться",
                    "web_app": {"url": web_app_url},
                },
            },
        )
        if result.get("ok"):
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Menu Button → {web_app_url}")
            )
        else:
            self.stderr.write(
                self.style.ERROR(f"  ✗ Ошибка: {result.get('error') or result}")
            )

        self.stdout.write(self.style.SUCCESS("\nГотово."))

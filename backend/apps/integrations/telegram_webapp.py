"""
Валидация Telegram WebApp initData.

Telegram подписывает initData HMAC'ом, ключ которого — производная от
TELEGRAM_BOT_TOKEN. Эту подпись надо проверить — иначе клиент мог бы
подделать chat_id и записаться от чужого имени.

Алгоритм описан в документации:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from urllib.parse import parse_qsl

from django.conf import settings

logger = logging.getLogger(__name__)


def verify_init_data(init_data: str, max_age_seconds: int = 86400) -> dict | None:
    """
    Проверяет подпись initData и возвращает распарсенные поля,
    либо None если подпись неверная или данные просрочены.

    init_data — это строка как `query_string`, которую Telegram передаёт
    через `Telegram.WebApp.initData`.
    """
    if not init_data:
        return None

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.error("verify_init_data: TELEGRAM_BOT_TOKEN не задан")
        return None

    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    # Проверка возраста
    auth_date = parsed.get("auth_date")
    if auth_date:
        try:
            import time

            age = int(time.time()) - int(auth_date)
            if age > max_age_seconds:
                logger.warning(f"initData expired: {age}s old")
                return None
        except (ValueError, TypeError):
            return None

    # data-check-string — отсортированные пары key=value, разделённые \n
    data_check_string = "\n".join(
        f"{key}={parsed[key]}" for key in sorted(parsed.keys())
    )

    # secret_key = HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        b"WebAppData", token.encode("utf-8"), hashlib.sha256
    ).digest()

    # вычисляем hash и сравниваем
    computed_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    # Распарсим вложенный user JSON если есть
    if "user" in parsed:
        import json

        try:
            parsed["user"] = json.loads(parsed["user"])
        except (json.JSONDecodeError, TypeError):
            pass

    return parsed


def extract_telegram_user(init_data: str) -> dict | None:
    """
    Возвращает {chat_id, first_name, last_name, username, language_code}
    или None если initData невалиден.

    chat_id у Telegram WebApp = user.id (это user_id, который для приватных
    чатов с ботом совпадает с chat_id).
    """
    data = verify_init_data(init_data)
    if not data:
        return None

    user = data.get("user")
    if not user or not isinstance(user, dict):
        return None

    chat_id = user.get("id")
    if not chat_id:
        return None

    return {
        "chat_id": str(chat_id),
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "username": user.get("username", ""),
        "language_code": user.get("language_code", ""),
    }

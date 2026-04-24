"""
Telegram transport — низкоуровневые HTTP-вызовы Bot API.
Не содержит бизнес-логики, только отправка сообщений и файлов.
"""
from __future__ import annotations

import json
import logging
import mimetypes
import os
from urllib import error, parse, request

from django.conf import settings

logger = logging.getLogger("apps.notifications.transports.telegram")


def is_configured() -> bool:
    return bool(
        getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        and getattr(settings, "TELEGRAM_CHAT_ID", "")
    )


def _api_url(method: str) -> str:
    token = settings.TELEGRAM_BOT_TOKEN
    return f"https://api.telegram.org/bot{token}/{method}"


def send_message(
    chat_id: str,
    text: str,
    reply_markup: dict | None = None,
) -> tuple[bool, str, str]:
    """
    Отправляет текстовое сообщение в указанный chat_id.
    reply_markup — опциональная inline/reply-клавиатура.
    Возвращает (success, message_id, error_text).
    """
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return False, "", "Telegram is not configured"

    params: dict = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup is not None:
        params["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)

    payload = parse.urlencode(params).encode("utf-8")
    req = request.Request(_api_url("sendMessage"), data=payload, method="POST")

    try:
        with request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data.get("ok"):
            return False, "", json.dumps(data, ensure_ascii=False)

        message_id = str(data.get("result", {}).get("message_id", ""))
        return True, message_id, ""

    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return False, "", f"HTTPError {exc.code}: {body}"
    except Exception as exc:
        logger.exception("Telegram send_message error: %s", exc)
        return False, "", str(exc)


def send_to_doctor(text: str) -> tuple[bool, str, str]:
    """Отправляет сообщение в основной чат врача."""
    if not is_configured():
        return False, "", "Telegram is not configured"
    return send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)


def send_file(
    file_path: str,
    chat_id: str,
    caption: str = "",
) -> tuple[bool, str, str]:
    """
    Отправляет файл (фото или документ) в указанный chat_id.
    Возвращает (success, message_id, error_text).
    """
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return False, "", "Telegram is not configured"

    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(filename)
    mime_type = mime_type or "application/octet-stream"

    is_image = mime_type.startswith("image/")
    method = "sendPhoto" if is_image else "sendDocument"
    file_field = "photo" if is_image else "document"

    import secrets as _secrets
    boundary = _secrets.token_hex(16)
    body = bytearray()

    def _add_text(name: str, value: str) -> None:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(f"{value}\r\n".encode())

    _add_text("chat_id", str(chat_id))
    if caption:
        _add_text("caption", caption)
        _add_text("parse_mode", "HTML")

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode()
    )
    body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode())
    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    req = request.Request(
        _api_url(method),
        data=bytes(body),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    try:
        with request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data.get("ok"):
            return False, "", json.dumps(data, ensure_ascii=False)

        message_id = str(data.get("result", {}).get("message_id", ""))
        return True, message_id, ""

    except error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore")
        return False, "", f"HTTPError {exc.code}: {body_text}"
    except Exception as exc:
        logger.exception("Telegram send_file error: %s", exc)
        return False, "", str(exc)

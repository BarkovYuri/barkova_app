"""
VK transport — низкоуровневые HTTP-вызовы VK API.
Не содержит бизнес-логики, только отправка сообщений и проверка прав.
"""
from __future__ import annotations

import json
import logging
import time
from urllib import error, parse, request

from django.conf import settings

logger = logging.getLogger("apps.notifications.transports.vk")


def is_configured() -> bool:
    return bool(
        getattr(settings, "VK_GROUP_TOKEN", "")
        and getattr(settings, "VK_GROUP_ID", "")
    )


def _api_url(method: str) -> str:
    return f"https://api.vk.com/method/{method}"


def _call(method: str, payload: dict) -> tuple[bool, dict, str]:
    """
    Базовый вызов VK API.
    Возвращает (success, result_dict, error_text).
    """
    token = getattr(settings, "VK_GROUP_TOKEN", "")
    if not token:
        return False, {}, "VK is not configured"

    data = {**payload, "access_token": token, "v": "5.199"}
    encoded = parse.urlencode(data).encode("utf-8")
    req = request.Request(_api_url(method), data=encoded, method="POST")

    try:
        with request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))

        if "error" in result:
            return False, result, json.dumps(result, ensure_ascii=False)

        return True, result, ""

    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return False, {}, f"HTTPError {exc.code}: {body}"
    except Exception as exc:
        logger.exception("VK API error (%s): %s", method, exc)
        return False, {}, str(exc)


def send_message(
    peer_id: str,
    text: str,
    keyboard: dict | None = None,
) -> tuple[bool, str, str]:
    """
    Отправляет сообщение в VK-диалог peer_id.
    keyboard — опциональная VK-клавиатура (dict).
    Возвращает (success, message_id, error_text).
    """
    if not is_configured() or not peer_id:
        return False, "", "VK is not configured"

    payload: dict = {
        "peer_id": str(peer_id),
        "message": text,
        "random_id": int(time.time() * 1000),
    }
    if keyboard is not None:
        payload["keyboard"] = json.dumps(keyboard, ensure_ascii=False)

    success, result, error_text = _call("messages.send", payload)
    if not success:
        return False, "", error_text

    message_id = str(result.get("response", ""))
    return True, message_id, ""


def is_messages_allowed(user_id: str) -> tuple[bool, str]:
    """
    Проверяет, может ли сообщество писать пользователю.
    Возвращает (allowed, error_text).
    """
    if not is_configured() or not user_id:
        return False, "VK user id is missing"

    success, result, error_text = _call(
        "messages.isMessagesFromGroupAllowed",
        {"group_id": settings.VK_GROUP_ID, "user_id": str(user_id)},
    )
    if not success:
        return False, error_text

    is_allowed = bool(result.get("response", {}).get("is_allowed"))
    return is_allowed, ""

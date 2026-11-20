"""
VK transport — низкоуровневые вызовы VK API от имени сообщества.

Не содержит бизнес-логики. Это единственный HTTP-клиент VK в проекте:
им пользуются и уведомления, и бот.
"""

from __future__ import annotations

import json
import logging
import re
import secrets
from urllib import error, parse, request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("apps.notifications.transports.vk")

# VK не поддерживает HTML в тексте сообщения. Шаблоны пишем plain-text,
# но на всякий случай вырезаем теги, чтобы они не попали в чат как есть.
_HTML_TAG_RE = re.compile(r"<[^>]+>")

# Сколько помним id сообщений, отправленных ботом. Нужно, чтобы отличать
# в событии message_reply ответ бота от ручного ответа врача.
_BOT_SENT_TTL = 60 * 60
# Пока бот отправляет сообщение, событие message_reply может прийти раньше,
# чем messages.send вернёт id. На это окно ставим флаг «бот пишет».
_BOT_SENDING_TTL = 30

MAX_MESSAGE_LENGTH = 4000


def _strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub("", text)


def is_configured() -> bool:
    return bool(getattr(settings, "VK_GROUP_TOKEN", "") and getattr(settings, "VK_GROUP_ID", ""))


def group_id() -> str:
    return str(getattr(settings, "VK_GROUP_ID", "") or "")


def call(method: str, payload: dict) -> tuple[bool, dict, str]:
    """
    Базовый вызов VK API. Возвращает (success, result_dict, error_text).

    VK отвечает HTTP 200 даже на ошибки, поэтому успех определяется
    отсутствием поля "error" в ответе.
    """
    token = getattr(settings, "VK_GROUP_TOKEN", "")
    if not token:
        return False, {}, "VK is not configured"

    data = {
        **{k: v for k, v in payload.items() if v is not None},
        "access_token": token,
        "v": getattr(settings, "VK_API_VERSION", "5.199"),
    }
    encoded = parse.urlencode(data).encode("utf-8")
    req = request.Request(f"https://api.vk.com/method/{method}", data=encoded, method="POST")
    timeout = getattr(settings, "VK_API_TIMEOUT", 15)

    try:
        with request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        logger.warning("VK API HTTP error (%s): %s %s", method, exc.code, body[:500])
        return False, {}, f"HTTPError {exc.code}: {body}"
    except Exception as exc:
        logger.warning("VK API network error (%s): %s", method, exc)
        return False, {}, str(exc)

    if "error" in result:
        err = result["error"]
        logger.warning(
            "VK API error (%s): code=%s msg=%s",
            method,
            err.get("error_code"),
            err.get("error_msg"),
        )
        return False, result, json.dumps(err, ensure_ascii=False)

    return True, result, ""


def is_permanent_error(error_text: str) -> bool:
    """Ошибки, при которых повтор отправки бессмыслен."""
    # 901 — пользователь запретил сообщения от сообщества,
    # 900/902 — пользователь в чёрном списке / настройки приватности,
    # 7 — нет прав у токена, 5 — неверный токен.
    return any(f'"error_code": {code}' in (error_text or "") for code in (5, 7, 900, 901, 902))


# ─── Сообщения ────────────────────────────────────────────────────────────────


def _bot_sent_key(message_id: str) -> str:
    return f"vk_bot_sent:{message_id}"


def _bot_sending_key(peer_id: str) -> str:
    return f"vk_bot_sending:{peer_id}"


def send_message(
    peer_id: str | int,
    text: str,
    keyboard: dict | None = None,
) -> tuple[bool, str, str]:
    """
    Отправляет сообщение в диалог peer_id от имени сообщества.
    Возвращает (success, message_id, error_text).
    """
    if not is_configured() or not peer_id:
        return False, "", "VK is not configured"

    clean_text = _strip_html(text)
    if len(clean_text) > MAX_MESSAGE_LENGTH:
        clean_text = clean_text[: MAX_MESSAGE_LENGTH - 2] + "\n…"

    payload: dict = {
        "peer_id": str(peer_id),
        "message": clean_text,
        # random_id защищает от дублей при повторной отправке; он должен
        # быть уникальным, а не «текущее время в мс».
        "random_id": secrets.randbits(31),
        "dont_parse_links": 0,
    }
    if keyboard is not None:
        payload["keyboard"] = json.dumps(keyboard, ensure_ascii=False)

    cache.set(_bot_sending_key(str(peer_id)), "1", timeout=_BOT_SENDING_TTL)
    try:
        success, result, error_text = call("messages.send", payload)
    finally:
        cache.delete(_bot_sending_key(str(peer_id)))

    if not success:
        return False, "", error_text

    message_id = str(result.get("response", ""))
    if message_id:
        cache.set(_bot_sent_key(message_id), "1", timeout=_BOT_SENT_TTL)
    return True, message_id, ""


def was_sent_by_bot(message_id: str | int | None, peer_id: str | int | None) -> bool:
    """True, если сообщение отправил наш код через API, а не человек."""
    if message_id and cache.get(_bot_sent_key(str(message_id))):
        return True
    return bool(peer_id and cache.get(_bot_sending_key(str(peer_id))))


def is_messages_allowed(user_id: str | int) -> tuple[bool, str]:
    """Может ли сообщество писать пользователю. Возвращает (allowed, error_text)."""
    if not is_configured() or not user_id:
        return False, "VK user id is missing"

    success, result, error_text = call(
        "messages.isMessagesFromGroupAllowed",
        {"group_id": group_id(), "user_id": str(user_id)},
    )
    if not success:
        return False, error_text

    return bool(result.get("response", {}).get("is_allowed")), ""


def answer_message_event(event_id: str, user_id: str | int, peer_id: str | int, text: str) -> None:
    """Показывает пользователю всплывающую подсказку после нажатия callback-кнопки."""
    call(
        "messages.sendMessageEventAnswer",
        {
            "event_id": str(event_id),
            "user_id": str(user_id),
            "peer_id": str(peer_id),
            "event_data": json.dumps({"type": "show_snackbar", "text": text[:90]}, ensure_ascii=False),
        },
    )


def mark_unanswered(peer_id: str | int) -> bool:
    """
    Возвращает диалог в «Неотвеченные» в интерфейсе сообщения сообщества.

    Любой ответ от имени сообщества, в том числе автоматический ответ бота,
    переводит диалог в отвеченные, и врач перестаёт его видеть. После
    автоответа диалог нужно явно вернуть в неотвеченные.
    """
    success, _, _ = call(
        "messages.markAsAnsweredDialog",
        {"peer_id": str(peer_id), "answered": 0, "group_id": group_id()},
    )
    return success


def get_user_names(user_ids: list[str | int]) -> dict[str, str]:
    """{"123": "Иван Петров"} для списка id. При ошибке — пустой словарь."""
    ids = [str(u) for u in user_ids if u]
    if not ids:
        return {}
    success, result, _ = call("users.get", {"user_ids": ",".join(ids)})
    if not success:
        return {}
    names: dict[str, str] = {}
    for user in result.get("response", []) or []:
        full = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        names[str(user.get("id"))] = full
    return names


def get_unanswered_conversations(count: int = 50) -> tuple[bool, list[dict]]:
    """Диалоги сообщества, помеченные как неотвеченные."""
    success, result, _ = call(
        "messages.getConversations",
        {"filter": "unanswered", "count": count, "group_id": group_id(), "extended": 0},
    )
    if not success:
        return False, []
    return True, result.get("response", {}).get("items", []) or []


# ─── Ссылки ───────────────────────────────────────────────────────────────────


def community_dialog_url() -> str:
    """Ссылка для пациента: открыть диалог с сообществом."""
    domain = getattr(settings, "VK_GROUP_DOMAIN", "")
    if domain:
        return f"https://vk.me/{domain}"
    return f"https://vk.com/im?sel=-{group_id()}"


def admin_dialog_url(peer_id: str | int) -> str:
    """Ссылка для врача: открыть этот диалог в интерфейсе сообщений сообщества."""
    return f"https://vk.com/gim{group_id()}?sel={peer_id}"

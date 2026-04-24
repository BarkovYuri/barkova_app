"""
LinkingService — единый сервис связывания пациента с мессенджером.

Заменяет четыре разрозненных потока:
  1. TelegramPrelink  (telegram/prelink/ + telegram/link/)
  2. VKPrelink        (vk/prelink/ + vk/link/)
  3. VKAutoLink       (vk/auto-link/)
  4. VKPendingLink    (vk/pending-link/)
"""
from __future__ import annotations

import logging

from django.core.cache import cache
from django.utils import timezone

from apps.notifications.models import TelegramPrelink, VKPrelink
from apps.appointments.models import Appointment

logger = logging.getLogger("apps.appointments.services.linking")


# ─── Telegram ────────────────────────────────────────────────────────────────

def create_telegram_prelink(bot_username: str) -> dict:
    """Создаёт prelink-токен и возвращает ссылку на бота."""
    import secrets
    token = secrets.token_urlsafe(16)
    prelink = TelegramPrelink.objects.create(token=token)
    bot_url = f"https://t.me/{bot_username}?start=connect_{token}"
    return {"token": prelink.token, "bot_url": bot_url}


def confirm_telegram_prelink(token: str, chat_id: str) -> tuple[bool, str]:
    """
    Вызывается ботом: привязывает chat_id к prelink-токену.
    Возвращает (success, error_message).
    """
    if not token or not chat_id:
        return False, "token и chat_id обязательны"

    prelink = TelegramPrelink.objects.filter(token=token, is_used=False).first()
    if not prelink:
        return False, "Токен не найден"

    prelink.chat_id = chat_id
    prelink.linked_at = timezone.now()
    prelink.save(update_fields=["chat_id", "linked_at"])
    return True, ""


def get_telegram_prelink_status(token: str) -> dict | None:
    """Возвращает статус prelink или None если не найден."""
    prelink = TelegramPrelink.objects.filter(token=token).first()
    if not prelink:
        return None
    return {"linked": bool(prelink.chat_id), "chat_id": prelink.chat_id}


# ─── VK Prelink ───────────────────────────────────────────────────────────────

def create_vk_prelink(group_id: str) -> dict:
    """Создаёт VK prelink-токен и возвращает ссылку на диалог."""
    import secrets
    token = secrets.token_urlsafe(16)
    prelink = VKPrelink.objects.create(token=token)
    vk_url = f"https://vk.com/im?sel=-{group_id}"
    return {"token": prelink.token, "vk_url": vk_url}


def confirm_vk_prelink(token: str, user_id: str, peer_id: str) -> tuple[bool, str]:
    """
    Вызывается VK-ботом: привязывает user_id/peer_id к prelink-токену.
    Возвращает (success, error_message).
    """
    if not token or not user_id or not peer_id:
        return False, "token, user_id и peer_id обязательны"

    prelink = VKPrelink.objects.filter(token=token, is_used=False).first()
    if not prelink:
        return False, "Токен не найден"

    prelink.user_id = user_id
    prelink.peer_id = peer_id
    prelink.linked_at = timezone.now()
    prelink.save(update_fields=["user_id", "peer_id", "linked_at"])
    return True, ""


def get_vk_prelink_status(token: str) -> dict | None:
    """Возвращает статус VK prelink или None если не найден."""
    prelink = VKPrelink.objects.filter(token=token).first()
    if not prelink:
        return None
    return {
        "linked": bool(prelink.user_id and prelink.peer_id),
        "user_id": prelink.user_id,
        "peer_id": prelink.peer_id,
    }


# ─── VK Pending Link (через VK ID flow) ──────────────────────────────────────

_VK_PENDING_CACHE_TTL = 15 * 60  # 15 минут


def create_vk_pending_link(vk_user_id: str, group_id: str) -> dict:
    """
    Записывает в кэш намерение пользователя связать VK ID.
    Когда он напишет боту, VKAutoLink его подхватит.
    """
    cache_key = f"vk_pending_link:{vk_user_id}"
    cache.set(cache_key, {"vk_user_id": vk_user_id}, timeout=_VK_PENDING_CACHE_TTL)
    dialog_url = f"https://vk.com/im?sel=-{group_id}"
    return {"status": "pending", "vk_user_id": vk_user_id, "dialog_url": dialog_url}


def resolve_vk_auto_link(user_id: str, peer_id: str) -> str:
    """
    Вызывается VK-ботом при входящем сообщении: если есть pending-запись
    в кэше, обновляет peer_id у последней записи пациента.
    Возвращает статус: 'linked' | 'not_pending' | 'no_appointment'.
    """
    cache_key = f"vk_pending_link:{user_id}"
    pending = cache.get(cache_key)
    if not pending:
        return "not_pending"

    appointment = (
        Appointment.objects.filter(vk_user_id=user_id)
        .order_by("-created_at")
        .first()
    )
    if not appointment:
        return "no_appointment"

    if appointment.vk_peer_id != peer_id:
        appointment.vk_peer_id = peer_id
        appointment.vk_linked_at = timezone.now()
        appointment.save(update_fields=["vk_peer_id", "vk_linked_at"])

    cache.delete(cache_key)
    logger.info("VK auto-link resolved: user=%s peer=%s appointment=%s", user_id, peer_id, appointment.id)
    return "linked"

"""
VK-бот сообщества. Работает через Callback API: VKCallbackView кладёт
событие в Celery, задача вызывает handle_event().

Главные правила, ради которых бот переписан:

1. Бот не «съедает» диалоги. Любой ответ от имени сообщества переводит
   диалог в «отвеченные», и врач его не видит. Поэтому на свободный текст
   бот отвечает только приветствием, не чаще раза в
   VK_BOT_GREETING_COOLDOWN_DAYS, и сразу возвращает диалог в неотвеченные.
2. О каждом сообщении человека врач получает алерт в личку VK, не чаще
   раза в VK_DOCTOR_ALERT_COOLDOWN_MINUTES на собеседника.
3. Если врач ответил в диалоге вручную (событие message_reply), бот молчит
   в этом диалоге VK_BOT_OPERATOR_PAUSE_HOURS.
4. Если пациент записался, но сообщество ещё не могло ему писать,
   подтверждение с кнопками уходит, как только он напишет или разрешит
   сообщения.
5. Кнопки работают с той записью, которая указана в кнопке, а не с
   «последней активной».
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.appointments.models import ACTIVE_STATUSES, Appointment

from . import notifiers
from .keyboards import vk as vk_kb
from .messages import doctor as doctor_msg
from .messages import patient as patient_msg
from .models import VKDialogState
from .transports import vk as vk_transport
from .vk_constants import (
    VK_CMD_CANCEL,
    VK_CMD_CANCEL_CONFIRM,
    VK_CMD_CANCEL_KEEP,
    VK_CMD_CANCEL_REQUEST,
    VK_CMD_CONFIRM,
    VK_CMD_DOCTOR,
    VK_CMD_FAQ,
    VK_CMD_MANAGE,
    VK_CMD_NO,
    VK_CMD_RESCHEDULE_REQUEST,
    VK_CMD_RESCHEDULE_TO,
    VK_CMD_YES,
    VK_MENU_KIND_ACTIVE_ROOT,
    VK_MENU_KIND_BOOKING,
    VK_MENU_KIND_CANCEL_CONFIRM,
    VK_MENU_KIND_MANAGE,
    VK_STATE_CONFIRM_CANCEL,
    VK_STATE_HAS_ACTIVE_APPOINTMENT,
)

logger = logging.getLogger("apps.notifications.vk_bot")

# peer_id бесед начинается с 2e9. Бот работает только в личных диалогах.
_CHAT_PEER_MIN = 2_000_000_000

_ACTION_COMMANDS = {VK_CMD_CONFIRM, VK_CMD_CANCEL, VK_CMD_YES, VK_CMD_NO, VK_CMD_DOCTOR}

_ATTACHMENT_NAMES = {
    "photo": "фото",
    "doc": "файл",
    "audio_message": "голосовое",
    "video": "видео",
    "audio": "аудио",
    "sticker": "стикер",
    "link": "ссылка",
    "wall": "запись со стены",
}


# ─── Диспетчер ────────────────────────────────────────────────────────────────


def handle_event(event: dict) -> None:
    event_type = event.get("type")
    obj = event.get("object") or {}
    if event_type == "message_new":
        handle_message_new(obj.get("message") or {})
    elif event_type == "message_reply":
        handle_message_reply(obj)
    elif event_type == "message_event":
        handle_message_event(obj)
    elif event_type == "message_allow":
        handle_message_allow(obj)


# ─── Вспомогательное ──────────────────────────────────────────────────────────


def _doctor_ids() -> set[str]:
    return {str(uid) for uid in getattr(settings, "VK_DOCTOR_USER_IDS", []) or []}


def _is_private_peer(peer_id: Any) -> bool:
    try:
        return 0 < int(peer_id) < _CHAT_PEER_MIN
    except (TypeError, ValueError):
        return False


def parse_payload(raw: Any) -> dict | None:
    if not raw:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def is_meaningful_text(text: str) -> bool:
    """Есть ли смысл приветствовать: отсекаем «ок», «😂» и подобные реакции."""
    return sum(1 for ch in text or "" if ch.isalpha()) >= 4


def attachments_summary(message: dict) -> str:
    counts = Counter(a.get("type", "") for a in message.get("attachments") or [])
    parts = []
    for kind, count in counts.items():
        name = _ATTACHMENT_NAMES.get(kind, kind or "вложение")
        parts.append(f"{name} ×{count}" if count > 1 else name)
    return ", ".join(parts)


def _get_state(user_id: str, peer_id: str) -> VKDialogState:
    state, _ = VKDialogState.objects.get_or_create(user_id=user_id, defaults={"peer_id": peer_id})
    if state.peer_id != peer_id:
        state.peer_id = peer_id
        state.save(update_fields=["peer_id", "updated_at"])
    return state


def _operator_active(state: VKDialogState) -> bool:
    return bool(state.operator_paused_until and state.operator_paused_until > timezone.now())


def _greeting_allowed(state: VKDialogState) -> bool:
    if state.last_menu_kind != VK_MENU_KIND_BOOKING or not state.last_menu_sent_at:
        return True
    cooldown = timedelta(days=settings.VK_BOT_GREETING_COOLDOWN_DAYS)
    return timezone.now() - state.last_menu_sent_at >= cooldown


def _mark_menu(state: VKDialogState, kind: str, appointment=None, dialog_state: str | None = None) -> None:
    state.last_menu_kind = kind
    state.last_menu_sent_at = timezone.now()
    fields = ["last_menu_kind", "last_menu_sent_at", "updated_at"]
    if appointment is not None:
        state.appointment = appointment
        fields.append("appointment")
    if dialog_state is not None:
        state.state = dialog_state
        fields.append("state")
    state.save(update_fields=fields)


def upcoming_active_appointments(user_id: str):
    """Активные записи пациента на сегодня и позже, ближайшие первыми."""
    return (
        Appointment.objects.select_related("slot")
        .filter(vk_user_id=str(user_id), status__in=ACTIVE_STATUSES, slot__date__gte=timezone.localdate())
        .order_by("slot__date", "slot__start_time")
    )


def deliver_pending_booking_messages(user_id: str) -> int:
    """Досылает подтверждения записей, которые не удалось отправить сразу."""
    sent = 0
    for appointment in upcoming_active_appointments(user_id).filter(patient_notified_at__isnull=True):
        ok, _ = notifiers.send_booking_created_to_patient(appointment)
        sent += int(ok)
    return sent


def _alert_doctor_about_message(user_id: str, peer_id: str, message: dict, appointment) -> None:
    cooldown = settings.VK_DOCTOR_ALERT_COOLDOWN_MINUTES * 60
    # cache.add атомарен: из нескольких одновременных сообщений алерт
    # отправит только первое.
    if not cache.add(f"vk_doctor_alert:{user_id}", "1", timeout=cooldown):
        return
    sender_name = vk_transport.get_user_names([user_id]).get(user_id, "")
    text = doctor_msg.incoming_message(
        sender_name=sender_name,
        user_id=user_id,
        text=(message.get("text") or "").strip(),
        attachments_summary=attachments_summary(message),
        appointment=appointment,
        dialog_url=vk_transport.admin_dialog_url(peer_id),
    )
    notifiers.alert_doctor(text, notification_type="incoming_message", appointment=appointment)


# ─── Рабочие часы и быстрые ответы ────────────────────────────────────────────


def _working_hours() -> tuple[int, int, str]:
    """(начало в минутах, конец в минутах, «09:00») из VK_BOT_WORKING_HOURS="09:00-21:00"."""
    raw = getattr(settings, "VK_BOT_WORKING_HOURS", "09:00-21:00") or "09:00-21:00"
    try:
        start, end = (part.strip() for part in raw.split("-", 1))
        sh, sm = (int(x) for x in start.split(":"))
        eh, em = (int(x) for x in end.split(":"))
        return sh * 60 + sm, eh * 60 + em, f"{sh:02d}:{sm:02d}"
    except ValueError:
        return 9 * 60, 21 * 60, "09:00"


def is_off_hours(now=None) -> bool:
    start, end, _ = _working_hours()
    local = timezone.localtime(now or timezone.now())
    minutes = local.hour * 60 + local.minute
    return not (start <= minutes < end)


def _off_hours_reply_allowed(user_id: str) -> bool:
    """Не чаще раза в 12 часов на человека: одной ночи — одно сообщение."""
    return cache.add(f"vk_off_hours:{user_id}", "1", timeout=12 * 60 * 60)


def bot_faq_items():
    from apps.content.models import FaqItem

    return list(FaqItem.objects.filter(is_active=True).exclude(bot_label="").order_by("order", "id")[:8])


def _answer_faq(peer: str, faq_id) -> None:
    from apps.content.models import FaqItem

    item = FaqItem.objects.filter(pk=faq_id, is_active=True).first()
    if item is None:
        return
    vk_transport.send_message(
        peer, patient_msg.faq_answer(item.question, item.answer), keyboard=vk_kb.welcome(bot_faq_items())
    )


# ─── message_new ──────────────────────────────────────────────────────────────


def handle_message_new(message: dict) -> None:
    peer_id = message.get("peer_id")
    from_id = message.get("from_id")
    if not from_id or int(from_id) <= 0 or not _is_private_peer(peer_id):
        return

    user_id, peer = str(from_id), str(peer_id)
    text = (message.get("text") or "").strip()
    payload = parse_payload(message.get("payload")) or {}

    if user_id in _doctor_ids():
        _handle_doctor_message(peer)
        return

    state = _get_state(user_id, peer)
    state.last_incoming_at = timezone.now()
    state.save(update_fields=["last_incoming_at", "updated_at"])

    # Кнопка быстрого ответа: отвечаем из FAQ, врача не беспокоим.
    if payload.get("cmd") == VK_CMD_FAQ:
        _answer_faq(peer, payload.get("id"))
        return

    # Пациент написал в сообщество: теперь ему можно писать, досылаем
    # подтверждения записей, которые не ушли сразу после бронирования.
    bot_replied = deliver_pending_booking_messages(user_id) > 0

    appointment = upcoming_active_appointments(user_id).first()
    is_start_button = payload.get("command") == "start"
    has_content = bool(text and not is_start_button) or bool(message.get("attachments"))

    operator_active = _operator_active(state)
    off_hours = is_off_hours()
    _, _, work_start = _working_hours()

    if (
        appointment is None
        and not operator_active
        and (is_start_button or is_meaningful_text(text))
        and _greeting_allowed(state)
    ):
        greeting = patient_msg.greeting()
        if off_hours and has_content and _off_hours_reply_allowed(user_id):
            greeting += "\n\n" + patient_msg.off_hours_note(work_start)
        ok, _, _ = vk_transport.send_message(peer, greeting, keyboard=vk_kb.welcome(bot_faq_items()))
        if ok:
            _mark_menu(state, VK_MENU_KIND_BOOKING)
            bot_replied = True
    elif has_content and off_hours and not operator_active and _off_hours_reply_allowed(user_id):
        # Ночью человек не должен думать, что его проигнорировали.
        ok, _, _ = vk_transport.send_message(peer, patient_msg.off_hours_note(work_start))
        bot_replied = bot_replied or ok

    if has_content:
        if bot_replied:
            # Автоответ перевёл диалог в «отвеченные». Возвращаем в
            # неотвеченные, иначе врач не увидит вопрос пациента.
            vk_transport.mark_unanswered(peer)
        _alert_doctor_about_message(user_id, peer, message, appointment)


def _handle_doctor_message(peer_id: str) -> None:
    """Врач пишет сообществу (например, чтобы разрешить алерты). Подтверждаем канал."""
    if not cache.add(f"vk_doctor_ping:{peer_id}", "1", timeout=10 * 60):
        return
    vk_transport.send_message(peer_id, doctor_msg.test_alert())


# ─── message_reply ────────────────────────────────────────────────────────────


def handle_message_reply(message: dict) -> None:
    """Исходящее сообщение сообщества. Если его написал человек, бот замолкает."""
    peer_id = message.get("peer_id")
    if not _is_private_peer(peer_id) or str(peer_id) in _doctor_ids():
        return
    written_by_admin = bool(message.get("admin_author_id"))
    if not written_by_admin and vk_transport.was_sent_by_bot(message.get("id"), peer_id):
        return

    pause_until = timezone.now() + timedelta(hours=settings.VK_BOT_OPERATOR_PAUSE_HOURS)
    state, _ = VKDialogState.objects.get_or_create(user_id=str(peer_id), defaults={"peer_id": str(peer_id)})
    state.operator_paused_until = pause_until
    state.save(update_fields=["operator_paused_until", "updated_at"])
    logger.info("VK operator replied to %s, bot paused until %s", peer_id, pause_until)


# ─── message_allow ────────────────────────────────────────────────────────────


def handle_message_allow(obj: dict) -> None:
    """Пациент разрешил сообщения от сообщества — досылаем подтверждение записи."""
    user_id = obj.get("user_id")
    if user_id:
        deliver_pending_booking_messages(str(user_id))


# ─── message_event (callback-кнопки) ─────────────────────────────────────────


def appointment_from_payload(user_id: str, payload: dict):
    """Запись из кнопки, если кнопка действительно принадлежит этому пользователю."""
    appointment_id = payload.get("appointment_id")
    token = str(payload.get("token") or "")
    if not appointment_id or not token:
        return None
    appointment = Appointment.objects.select_related("slot").filter(pk=appointment_id).first()
    if appointment is None or appointment.vk_link_token != token or str(appointment.vk_user_id) != str(user_id):
        return None
    return appointment


def handle_message_event(obj: dict) -> None:
    from apps.appointments.services.actions import AppointmentActionService

    event_id = obj.get("event_id")
    user_id = obj.get("user_id")
    peer_id = obj.get("peer_id")
    payload = parse_payload(obj.get("payload"))
    if not event_id or not user_id or not peer_id:
        return

    user, peer = str(user_id), str(peer_id)
    appointment = appointment_from_payload(user, payload or {})
    if appointment is None:
        vk_transport.answer_message_event(event_id, user, peer, "Запись не найдена")
        return
    vk_transport.answer_message_event(event_id, user, peer, "Обрабатываю…")

    cmd = (payload or {}).get("cmd")
    state = _get_state(user, peer)
    state.last_action_at = timezone.now()
    state.save(update_fields=["last_action_at", "updated_at"])

    if cmd in {VK_CMD_MANAGE, VK_CMD_CANCEL_REQUEST, VK_CMD_RESCHEDULE_REQUEST, VK_CMD_RESCHEDULE_TO} and not (
        appointment.is_active
    ):
        notifiers.send_to_patient_vk(appointment, patient_msg.action_not_allowed())
        return

    if cmd == VK_CMD_MANAGE:
        vk_transport.send_message(peer, patient_msg.manage_prompt(appointment), keyboard=vk_kb.manage(appointment))
        _mark_menu(state, VK_MENU_KIND_MANAGE, appointment, VK_STATE_HAS_ACTIVE_APPOINTMENT)
        return

    if cmd == VK_CMD_CANCEL_REQUEST:
        vk_transport.send_message(
            peer, patient_msg.cancel_confirm_prompt(appointment), keyboard=vk_kb.cancel_confirm(appointment)
        )
        _mark_menu(state, VK_MENU_KIND_CANCEL_CONFIRM, appointment, VK_STATE_CONFIRM_CANCEL)
        return

    if cmd == VK_CMD_RESCHEDULE_REQUEST:
        _offer_reschedule(appointment, user, peer)
        return

    if cmd == VK_CMD_RESCHEDULE_TO:
        _do_reschedule(appointment, (payload or {}).get("slot_id"), user, peer)
        return

    if cmd == VK_CMD_CANCEL_KEEP:
        vk_transport.send_message(peer, patient_msg.kept(appointment), keyboard=vk_kb.active_root(appointment))
        _mark_menu(state, VK_MENU_KIND_ACTIVE_ROOT, appointment, VK_STATE_HAS_ACTIVE_APPOINTMENT)
        return

    action = VK_CMD_CANCEL if cmd == VK_CMD_CANCEL_CONFIRM else cmd
    if action in _ACTION_COMMANDS:
        AppointmentActionService.handle(appointment, action)
        return

    logger.warning("Unknown VK button command: %s", cmd)


# ─── Перенос записи ───────────────────────────────────────────────────────────


def _offer_reschedule(appointment, user_id: str, peer: str) -> None:
    from apps.appointments.services.reschedule import reschedule_options

    slots = reschedule_options(appointment)
    if slots:
        vk_transport.send_message(
            peer, patient_msg.reschedule_prompt(appointment), keyboard=vk_kb.reschedule_options(appointment, slots)
        )
        return

    # Свободных слотов нет: передаём врачу, пусть подберёт время сам.
    vk_transport.send_message(peer, patient_msg.reschedule_no_slots(), keyboard=vk_kb.active_root(appointment))
    vk_transport.mark_unanswered(peer)
    notifiers.alert_doctor(
        doctor_msg.reschedule_without_slots(appointment, dialog_url=vk_transport.admin_dialog_url(peer)),
        notification_type="doctor_contact",
        appointment=appointment,
    )


def _do_reschedule(appointment, slot_id, user_id: str, peer: str) -> None:
    from apps.appointments.services.reschedule import RescheduleError, reschedule, reschedule_options
    from apps.appointments.services.status import SOURCE_PATIENT

    try:
        reschedule(appointment, int(slot_id), source=SOURCE_PATIENT)
    except (RescheduleError, TypeError, ValueError):
        slots = reschedule_options(appointment)
        keyboard = vk_kb.reschedule_options(appointment, slots) if slots else vk_kb.active_root(appointment)
        vk_transport.send_message(peer, patient_msg.reschedule_unavailable(), keyboard=keyboard)
        return
    appointment.refresh_from_db()
    vk_transport.send_message(peer, patient_msg.rescheduled(appointment), keyboard=vk_kb.active_root(appointment))

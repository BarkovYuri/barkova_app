"""Тесты VK-бота: врач не теряет диалоги, бот не перебивает живую переписку,
кнопки работают со своей записью, подтверждение досылается."""

import json
from datetime import time, timedelta

import pytest
from django.core import mail
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.notifications import vk_bot
from apps.notifications.models import NotificationLog, VKDialogState
from apps.notifications.notifiers import alert_doctor
from apps.scheduling.models import TimeSlot

DOCTOR_ID = "555"
PATIENT_ID = "777"

pytestmark = pytest.mark.django_db


@pytest.fixture
def doctor(settings):
    settings.VK_DOCTOR_USER_IDS = [DOCTOR_ID]
    settings.VK_DOCTOR_ALERT_COOLDOWN_MINUTES = 30
    settings.VK_BOT_GREETING_COOLDOWN_DAYS = 30
    settings.VK_BOT_OPERATOR_PAUSE_HOURS = 24


def _slot(days=2, hour=10):
    day = timezone.localdate() + timedelta(days=days)
    return TimeSlot.objects.create(
        date=day,
        start_time=time(hour, 0),
        end_time=time(hour, 30),
        is_booked=True,
    )


def _appointment(**kwargs):
    if "slot" not in kwargs:
        kwargs["slot"] = _slot()
    defaults = {
        "name": "Анна",
        "phone": "+79991234567",
        "consent_given": True,
        "privacy_accepted": True,
        "offer_accepted": True,
        "preferred_contact_method": "vk",
        "vk_user_id": PATIENT_ID,
        "vk_peer_id": PATIENT_ID,
        "vk_link_token": "tok",
    }
    defaults.update(kwargs)
    return Appointment.objects.create(**defaults)


def _message_new(text="Здравствуйте, сколько стоит разбор?", from_id=PATIENT_ID, **extra):
    message = {"id": 1, "peer_id": int(from_id), "from_id": int(from_id), "text": text, **extra}
    return {"type": "message_new", "object": {"message": message}}


def _event(cmd, appointment, token=None, user_id=PATIENT_ID):
    payload = {"cmd": cmd, "appointment_id": appointment.id, "token": token or appointment.vk_link_token}
    return {
        "type": "message_event",
        "object": {
            "event_id": "ev1",
            "user_id": int(user_id),
            "peer_id": int(user_id),
            "payload": payload,
        },
    }


# ─── Входящие сообщения ───────────────────────────────────────────────────────


def test_first_message_greets_returns_dialog_to_unanswered_and_alerts_doctor(fake_vk, doctor):
    vk_bot.handle_event(_message_new())

    patient_msgs = fake_vk.sent(PATIENT_ID)
    assert len(patient_msgs) == 1
    assert "Записаться на онлайн-разбор" in patient_msgs[0]["message"]
    # После автоответа диалог возвращён в «Неотвеченные».
    assert ("messages.markAsAnsweredDialog", {"peer_id": PATIENT_ID, "answered": 0, "group_id": "123"}) in fake_vk.calls
    # Врач получил алерт с текстом и ссылкой на диалог.
    doctor_msgs = fake_vk.sent(DOCTOR_ID)
    assert len(doctor_msgs) == 1
    assert "сколько стоит разбор" in doctor_msgs[0]["message"]
    assert f"gim123?sel={PATIENT_ID}" in doctor_msgs[0]["message"]
    assert "Иван Петров" in doctor_msgs[0]["message"]


def test_second_message_is_not_greeted_and_doctor_alert_is_throttled(fake_vk, doctor):
    vk_bot.handle_event(_message_new())
    vk_bot.handle_event(_message_new("И ещё вопрос про анализы"))

    assert len(fake_vk.sent(PATIENT_ID)) == 1
    assert len(fake_vk.sent(DOCTOR_ID)) == 1


def test_short_reaction_is_not_greeted_but_doctor_still_alerted(fake_vk, doctor):
    vk_bot.handle_event(_message_new("ок"))

    assert fake_vk.sent(PATIENT_ID) == []
    assert "markAsAnsweredDialog" not in " ".join(fake_vk.methods())
    assert len(fake_vk.sent(DOCTOR_ID)) == 1


def test_photo_without_text_alerts_doctor(fake_vk, doctor):
    vk_bot.handle_event(_message_new("", attachments=[{"type": "photo"}, {"type": "photo"}]))

    assert "фото ×2" in fake_vk.sent(DOCTOR_ID)[0]["message"]


def test_manual_doctor_reply_pauses_bot(fake_vk, doctor):
    reply = {"type": "message_reply", "object": {"id": 42, "peer_id": int(PATIENT_ID), "admin_author_id": 1}}
    vk_bot.handle_event(reply)

    state = VKDialogState.objects.get(user_id=PATIENT_ID)
    assert state.operator_paused_until > timezone.now()

    vk_bot.handle_event(_message_new("Спасибо, а когда можно прийти?"))
    # Бот не вмешивается в живую переписку, но врач о сообщении знает.
    assert fake_vk.sent(PATIENT_ID) == []
    assert len(fake_vk.sent(DOCTOR_ID)) == 1


def test_bot_own_reply_does_not_pause_bot(fake_vk, doctor):
    vk_bot.handle_event(_message_new())
    bot_message_id = 1000  # первый id из FakeVK — приветствие бота
    vk_bot.handle_event({"type": "message_reply", "object": {"id": bot_message_id, "peer_id": int(PATIENT_ID)}})

    state = VKDialogState.objects.get(user_id=PATIENT_ID)
    assert state.operator_paused_until is None


def test_doctor_writing_to_community_gets_confirmation_not_greeting(fake_vk, doctor):
    vk_bot.handle_event(_message_new("тест", from_id=DOCTOR_ID))

    sent = fake_vk.sent(DOCTOR_ID)
    assert len(sent) == 1
    assert "Проверка оповещений" in sent[0]["message"]


def test_group_chats_are_ignored(fake_vk, doctor):
    message = {"id": 1, "peer_id": 2000000001, "from_id": int(PATIENT_ID), "text": "Всем привет из беседы"}
    vk_bot.handle_event({"type": "message_new", "object": {"message": message}})
    assert fake_vk.calls == []


# ─── Отложенная доставка подтверждения ────────────────────────────────────────


def test_pending_booking_message_is_delivered_when_patient_writes(fake_vk, doctor):
    appointment = _appointment(patient_notified_at=None)

    vk_bot.handle_event(_message_new("Начать", payload=json.dumps({"command": "start"})))

    patient_msgs = fake_vk.sent(PATIENT_ID)
    assert len(patient_msgs) == 1
    assert "Вы записаны" in patient_msgs[0]["message"]
    appointment.refresh_from_db()
    assert appointment.patient_notified_at is not None
    # Кнопка «Начать» — не вопрос: врача не дёргаем.
    assert fake_vk.sent(DOCTOR_ID) == []


def test_pending_booking_message_is_delivered_on_message_allow(fake_vk, doctor):
    appointment = _appointment(patient_notified_at=None)

    vk_bot.handle_event({"type": "message_allow", "object": {"user_id": int(PATIENT_ID), "key": ""}})

    assert "Вы записаны" in fake_vk.sent(PATIENT_ID)[0]["message"]
    appointment.refresh_from_db()
    assert appointment.patient_notified_at is not None


def test_patient_with_appointment_question_is_forwarded_not_templated(fake_vk, doctor):
    _appointment(patient_notified_at=timezone.now())

    vk_bot.handle_event(_message_new("Можно перенести на другой день?"))

    assert fake_vk.sent(PATIENT_ID) == []
    doctor_text = fake_vk.sent(DOCTOR_ID)[0]["message"]
    assert "перенести" in doctor_text
    assert "У пациента есть запись" in doctor_text


# ─── Кнопки ───────────────────────────────────────────────────────────────────


def test_button_with_foreign_token_does_nothing(fake_vk, doctor):
    appointment = _appointment()

    vk_bot.handle_event(_event("cancel_confirm", appointment, token="wrong"))

    appointment.refresh_from_db()
    assert appointment.status == "new"
    answer = next(p for m, p in fake_vk.calls if m == "messages.sendMessageEventAnswer")
    assert "не найдена" in answer["event_data"]


def test_cancel_button_cancels_exactly_that_appointment_and_frees_slot(
    fake_vk, doctor, django_capture_on_commit_callbacks
):
    older = _appointment(slot=_slot(days=2), vk_link_token="tok-old")
    newer = _appointment(slot=_slot(days=5), vk_link_token="tok-new")

    with django_capture_on_commit_callbacks(execute=True):
        vk_bot.handle_event(_event("cancel_confirm", older))

    older.refresh_from_db()
    newer.refresh_from_db()
    assert older.status == "cancelled"
    assert newer.status == "new"
    assert older.slot.is_booked is False
    # Врачу ушёл алерт об отмене пациентом.
    assert any("отменил запись" in p["message"] for p in fake_vk.sent(DOCTOR_ID))


def test_doctor_button_alerts_doctor_and_keeps_dialog_unanswered(fake_vk, doctor):
    appointment = _appointment()

    vk_bot.handle_event(_event("doctor", appointment))

    assert any("просит связаться" in p["message"] for p in fake_vk.sent(DOCTOR_ID))
    assert ("messages.markAsAnsweredDialog", {"peer_id": PATIENT_ID, "answered": 0, "group_id": "123"}) in fake_vk.calls


# ─── Канал алертов врачу ──────────────────────────────────────────────────────


def test_doctor_alert_falls_back_to_email_when_vk_fails(fake_vk, settings):
    settings.VK_DOCTOR_USER_IDS = [DOCTOR_ID]
    settings.DOCTOR_ALERT_EMAILS = ["doctor@example.com"]
    fake_vk.fail_send_to = {DOCTOR_ID}

    assert alert_doctor("🆕 Новая запись\nтекст", notification_type="created") is True

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "🆕 Новая запись"
    statuses = set(NotificationLog.objects.values_list("channel", "status"))
    assert statuses == {("vk", "failed"), ("email", "sent")}


def test_doctor_alert_without_any_channel_reports_failure(fake_vk):
    assert alert_doctor("текст", notification_type="created") is False
    log = NotificationLog.objects.get()
    assert log.status == "failed" and "VK_DOCTOR_USER_IDS" in log.error_text


def test_new_appointment_alert_without_channels_fails_fast(fake_vk):
    from apps.notifications.tasks import alert_doctor_new_appointment

    appointment = _appointment()
    assert alert_doctor_new_appointment.delay(appointment.pk).get() is False
    log = NotificationLog.objects.get(notification_type="created")
    assert log.status == "failed" and log.recipient == "не настроено"


def test_alert_check_command_reports_without_sending(fake_vk, settings):
    from io import StringIO

    from django.core.management import call_command

    settings.VK_DOCTOR_USER_IDS = [DOCTOR_ID]
    out = StringIO()
    call_command("send_test_doctor_alert", "--check", stdout=out)

    assert "сообщество может писать" in out.getvalue()
    assert fake_vk.sent() == []


def test_alert_check_command_fails_when_nobody_reachable(fake_vk, settings):
    from django.core.management import call_command
    from django.core.management.base import CommandError

    settings.VK_DOCTOR_USER_IDS = [DOCTOR_ID]
    fake_vk.allowed = False
    with pytest.raises(CommandError):
        call_command("send_test_doctor_alert", "--check")

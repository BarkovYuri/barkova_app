"""Сквозные тесты записи: бронирование, смена статуса, админка, файлы,
Callback API, напоминания и часовой пояс."""

from datetime import datetime, time, timedelta
from unittest import mock

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.appointments.admin import AppointmentAdmin
from apps.appointments.models import Appointment, AppointmentAttachment
from apps.appointments.services.status import SOURCE_DOCTOR, SOURCE_PATIENT, change_status
from apps.scheduling.models import TimeSlot
from apps.scheduling.timefmt import msk_offset_hours, timezone_label

pytestmark = pytest.mark.django_db

DOCTOR_ID = "555"
PATIENT_ID = "777"


def _slot(days=3, hour=10, booked=False):
    return TimeSlot.objects.create(
        date=timezone.localdate() + timedelta(days=days),
        start_time=time(hour, 0),
        end_time=time(hour, 30),
        is_booked=booked,
    )


def _appointment(slot=None, **kwargs):
    slot = slot or _slot(booked=True)
    data = {
        "slot": slot,
        "name": "Анна",
        "phone": "+79991234567",
        "consent_given": True,
        "privacy_accepted": True,
        "offer_accepted": True,
        "preferred_contact_method": "vk",
        "vk_user_id": PATIENT_ID,
        "vk_peer_id": PATIENT_ID,
        "vk_link_token": "tok",
        "patient_notified_at": timezone.now(),
    }
    data.update(kwargs)
    return Appointment.objects.create(**data)


def _booking_payload(slot, **extra):
    data = {
        "slot_id": slot.id,
        "name": "Анна",
        "phone": "+7 (999) 123-45-67",
        "reason": "Вопрос по анализам",
        "consent_given": "true",
        "privacy_accepted": "true",
        "offer_accepted": "true",
    }
    data.update(extra)
    return data


@pytest.fixture
def doctor(settings):
    settings.VK_DOCTOR_USER_IDS = [DOCTOR_ID]


@pytest.fixture
def staff_user():
    return get_user_model().objects.create_user("doc", password="x-strong-pass-123", is_staff=True, is_superuser=True)


# ─── Бронирование через API ───────────────────────────────────────────────────


def test_booking_by_phone_without_vk_alerts_doctor(fake_vk, doctor, django_capture_on_commit_callbacks):
    slot = _slot()
    client = APIClient()

    with django_capture_on_commit_callbacks(execute=True):
        response = client.post(
            "/api/appointments/", _booking_payload(slot, preferred_contact_method="phone"), format="multipart"
        )

    assert response.status_code == 201, response.content
    body = response.json()
    # Публичный ответ без служебного токена кнопок и файлов.
    assert "vk_link_token" not in body and "attachments" not in body and "phone" not in body
    slot.refresh_from_db()
    assert slot.is_booked
    doctor_text = fake_vk.sent(DOCTOR_ID)[0]["message"]
    assert "Новая запись" in doctor_text and "VK пациента: не привязан" in doctor_text


def test_booking_with_vk_delivers_message_to_patient(fake_vk, doctor, django_capture_on_commit_callbacks):
    slot = _slot()
    with (
        mock.patch(
            "apps.appointments.serializers.verify_vk_id_token", return_value={"verified": True, "user_id": PATIENT_ID}
        ),
        django_capture_on_commit_callbacks(execute=True),
    ):
        response = APIClient().post(
            "/api/appointments/",
            _booking_payload(slot, preferred_contact_method="vk", vk_user_id=PATIENT_ID, vk_id_access_token="t"),
            format="multipart",
        )

    assert response.status_code == 201, response.content
    appointment = Appointment.objects.get()
    assert appointment.vk_user_id == PATIENT_ID
    assert appointment.patient_notified_at is not None
    assert "Вы записаны" in fake_vk.sent(PATIENT_ID)[0]["message"]


def test_booking_when_patient_has_not_allowed_messages_warns_doctor(
    fake_vk, doctor, django_capture_on_commit_callbacks
):
    fake_vk.allowed = False
    slot = _slot()
    with (
        mock.patch(
            "apps.appointments.serializers.verify_vk_id_token", return_value={"verified": True, "user_id": PATIENT_ID}
        ),
        django_capture_on_commit_callbacks(execute=True),
    ):
        APIClient().post(
            "/api/appointments/",
            _booking_payload(slot, preferred_contact_method="vk", vk_user_id=PATIENT_ID, vk_id_access_token="t"),
            format="multipart",
        )

    assert fake_vk.sent(PATIENT_ID) == []
    assert Appointment.objects.get().patient_notified_at is None
    assert "не разрешил сообщения" in fake_vk.sent(DOCTOR_ID)[0]["message"]


def test_vk_booking_requires_vk_id(fake_vk):
    response = APIClient().post(
        "/api/appointments/", _booking_payload(_slot(), preferred_contact_method="vk"), format="multipart"
    )
    assert response.status_code == 400
    assert "VK ID" in str(response.json())


def test_too_many_or_too_big_files_are_rejected(settings):
    settings.APPOINTMENT_MAX_FILES = 2
    settings.APPOINTMENT_MAX_FILE_MB = 1
    slot = _slot()
    files = [SimpleUploadedFile(f"a{i}.pdf", b"x") for i in range(3)]
    response = APIClient().post("/api/appointments/", {**_booking_payload(slot), "files": files}, format="multipart")
    assert response.status_code == 400
    big = SimpleUploadedFile("big.pdf", b"x" * (1024 * 1024 + 1))
    response = APIClient().post("/api/appointments/", {**_booking_payload(slot), "files": [big]}, format="multipart")
    assert response.status_code == 400


def test_uploaded_files_get_private_random_names(fake_vk, settings, tmp_path, django_capture_on_commit_callbacks):
    settings.MEDIA_ROOT = tmp_path
    slot = _slot()
    upload = SimpleUploadedFile("Иванов_анализы.pdf", b"%PDF-1.4", content_type="application/pdf")
    with django_capture_on_commit_callbacks(execute=True):
        response = APIClient().post(
            "/api/appointments/", {**_booking_payload(slot), "files": [upload]}, format="multipart"
        )
    assert response.status_code == 201, response.content
    name = AppointmentAttachment.objects.get().file.name
    assert name.startswith("private/appointments/") and name.endswith(".pdf")
    assert "Иванов" not in name


# ─── Сервис статусов ──────────────────────────────────────────────────────────


def test_cancel_frees_slot_and_reopen_books_it_again(fake_vk):
    appointment = _appointment()
    change_status(appointment, "cancelled", source=SOURCE_PATIENT)
    appointment.slot.refresh_from_db()
    assert appointment.slot.is_booked is False

    change_status(appointment, "new", source=SOURCE_DOCTOR)
    appointment.slot.refresh_from_db()
    assert appointment.slot.is_booked is True


def test_reopen_is_refused_when_slot_taken_by_another_patient(fake_vk):
    first = _appointment()
    change_status(first, "cancelled", source=SOURCE_PATIENT)
    _appointment(slot=first.slot, vk_user_id="888")

    with pytest.raises(ValidationError):
        change_status(first, "confirmed", source=SOURCE_DOCTOR)


def test_doctor_cancel_notifies_patient(fake_vk, django_capture_on_commit_callbacks):
    appointment = _appointment()
    with django_capture_on_commit_callbacks(execute=True):
        change_status(appointment, "cancelled", source=SOURCE_DOCTOR)
    assert "отменена врачом" in fake_vk.sent(PATIENT_ID)[0]["message"]


# ─── Django-админка ───────────────────────────────────────────────────────────


def _admin_request(user):
    request = RequestFactory().post("/admin/")
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


def test_admin_bulk_cancel_frees_slots(fake_vk, staff_user, django_capture_on_commit_callbacks):
    appointment = _appointment()
    model_admin = AppointmentAdmin(Appointment, AdminSite())

    with django_capture_on_commit_callbacks(execute=True):
        model_admin.mark_cancelled(_admin_request(staff_user), Appointment.objects.filter(pk=appointment.pk))

    appointment.refresh_from_db()
    appointment.slot.refresh_from_db()
    assert appointment.status == "cancelled"
    assert appointment.slot.is_booked is False
    assert "отменена врачом" in fake_vk.sent(PATIENT_ID)[0]["message"]


def test_admin_form_save_with_new_slot_syncs_both_slots(fake_vk, staff_user):
    appointment = _appointment()
    old_slot = appointment.slot
    new_slot = _slot(days=4)
    model_admin = AppointmentAdmin(Appointment, AdminSite())

    appointment.slot = new_slot
    model_admin.save_model(_admin_request(staff_user), appointment, form=None, change=True)

    old_slot.refresh_from_db()
    new_slot.refresh_from_db()
    assert old_slot.is_booked is False
    assert new_slot.is_booked is True


# ─── Защищённые файлы ─────────────────────────────────────────────────────────


def test_patient_files_require_staff(settings, tmp_path, staff_user):
    settings.MEDIA_ROOT = tmp_path
    settings.DEBUG = False
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "scan.pdf").write_bytes(b"%PDF")

    client = APIClient()
    anonymous = client.get("/admin/files/private/scan.pdf")
    assert anonymous.status_code == 302 and "/admin/login/" in anonymous["Location"]

    client.force_login(staff_user)
    response = client.get("/admin/files/private/scan.pdf")
    assert response.status_code == 200
    assert response["X-Accel-Redirect"] == "/_protected_media/private/scan.pdf"
    assert "no-store" in response["Cache-Control"]


def test_patient_files_path_traversal_is_blocked(settings, tmp_path, staff_user):
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()
    client.force_login(staff_user)
    assert client.get("/admin/files/../config/settings.py").status_code == 404


# ─── VK Callback API ──────────────────────────────────────────────────────────


def _callback(payload):
    return APIClient().post("/api/appointments/vk/callback/", payload, format="json")


def test_callback_rejects_wrong_secret_and_foreign_group(settings):
    settings.VK_CALLBACK_SECRET = "s3cret"
    base = {"type": "message_new", "object": {"message": {}}, "event_id": "e1"}
    assert _callback({**base, "group_id": 123, "secret": "nope"}).status_code == 403
    assert _callback({**base, "group_id": 999, "secret": "s3cret"}).status_code == 403


def test_callback_processes_event_once(settings, fake_vk, doctor):
    settings.VK_CALLBACK_SECRET = "s3cret"
    event = {
        "type": "message_new",
        "group_id": 123,
        "secret": "s3cret",
        "event_id": "dup-1",
        "object": {
            "message": {"id": 5, "peer_id": int(PATIENT_ID), "from_id": int(PATIENT_ID), "text": "Здравствуйте, вопрос"}
        },
    }
    assert _callback(event).content == b"ok"
    assert _callback(event).content == b"ok"
    assert len(fake_vk.sent(DOCTOR_ID)) == 1


def test_callback_asks_vk_to_retry_when_broker_is_down(settings):
    settings.VK_CALLBACK_SECRET = "s3cret"
    event = {"type": "message_new", "group_id": 123, "secret": "s3cret", "event_id": "e2", "object": {}}
    with mock.patch("apps.appointments.views.process_vk_callback_event.delay", side_effect=ConnectionError):
        assert _callback(event).status_code == 503
    # Ключ дедупликации снят: повтор от VK будет обработан.
    with mock.patch("apps.appointments.views.process_vk_callback_event.delay") as delay:
        assert _callback(event).status_code == 200
        delay.assert_called_once()


# ─── Напоминания и часовой пояс ───────────────────────────────────────────────


def test_timezone_label_for_tomsk(settings):
    settings.TIME_ZONE = "Asia/Tomsk"
    timezone.activate("Asia/Tomsk")
    try:
        assert msk_offset_hours() == 4
        assert timezone_label() == "по времени Томска (МСК+4)"
    finally:
        timezone.deactivate()


def test_reminder_is_sent_two_hours_before_in_schedule_timezone(fake_vk, settings):
    from apps.appointments.tasks import send_appointment_reminders

    local_now = timezone.localtime()
    start = (local_now + timedelta(hours=2)).replace(second=0, microsecond=0)
    slot = TimeSlot.objects.create(
        date=start.date(),
        start_time=start.time(),
        end_time=(start + timedelta(minutes=30)).time(),
        is_booked=True,
    )
    appointment = _appointment(slot=slot)
    Appointment.objects.filter(pk=appointment.pk).update(created_at=timezone.now() - timedelta(days=1))

    result = send_appointment_reminders()

    assert result["sent_ids"] == [appointment.id]
    assert "Напоминание" in fake_vk.sent(PATIENT_ID)[0]["message"]


def test_reminder_not_retried_forever_when_patient_blocked_messages(fake_vk, settings):
    from apps.appointments.tasks import send_appointment_reminders

    start = (timezone.localtime() + timedelta(hours=1, minutes=30)).replace(second=0, microsecond=0)
    slot = TimeSlot.objects.create(
        date=start.date(), start_time=start.time(), end_time=(start + timedelta(minutes=30)).time(), is_booked=True
    )
    appointment = _appointment(slot=slot)
    Appointment.objects.filter(pk=appointment.pk).update(created_at=timezone.now() - timedelta(days=1))
    fake_vk.fail_send_to = set()

    def blocked(method, payload):
        if method == "messages.send":
            return False, {}, '{"error_code": 901, "error_msg": "Can\'t send messages"}'
        return True, {"response": 1}, ""

    with mock.patch("apps.notifications.transports.vk.call", side_effect=blocked):
        send_appointment_reminders()

    appointment.refresh_from_db()
    assert appointment.reminder_sent_at is not None


def test_slots_api_returns_start_with_timezone(fake_vk):
    slot = _slot(days=3)
    response = APIClient().get(f"/api/available-slots/?date={slot.date.isoformat()}")
    assert response.status_code == 200
    starts_at = datetime.fromisoformat(response.json()[0]["starts_at"])
    assert starts_at.utcoffset() is not None

    assert APIClient().get("/api/available-slots/?date=garbage").status_code == 400
    info = APIClient().get("/api/schedule-info/").json()
    assert "label" in info and "msk_offset_hours" in info


def test_available_dates_skip_slots_starting_within_an_hour():
    now = timezone.localtime()
    soon = (now + timedelta(minutes=30)).replace(second=0, microsecond=0)
    TimeSlot.objects.create(date=soon.date(), start_time=soon.time(), end_time=(soon + timedelta(minutes=30)).time())
    later_slot = _slot(days=3)

    dates = APIClient().get("/api/available-dates/").json()

    assert [d["date"] for d in dates] == [later_slot.date.isoformat()]


def test_admin_when_filter_today(fake_vk, staff_user):
    from apps.appointments.admin import WhenFilter

    today_slot = TimeSlot.objects.create(
        date=timezone.localdate(), start_time=time(23, 0), end_time=time(23, 30), is_booked=True
    )
    today = _appointment(slot=today_slot)
    _appointment(slot=_slot(days=5), vk_user_id="888")

    request = _admin_request(staff_user)
    when = WhenFilter(request, {"when": ["today"]}, Appointment, AppointmentAdmin(Appointment, AdminSite()))
    assert list(when.queryset(request, Appointment.objects.all())) == [today]


def test_missing_doctor_profile_is_404_so_frontend_does_not_cache_it():
    assert APIClient().get("/api/profile/").status_code == 404


def test_admin_slot_change_notifies_patient_and_resets_reminder(
    fake_vk, staff_user, django_capture_on_commit_callbacks
):
    appointment = _appointment()
    Appointment.objects.filter(pk=appointment.pk).update(reminder_sent_at=timezone.now())
    appointment.refresh_from_db()
    new_slot = _slot(days=4)

    appointment.slot = new_slot
    with django_capture_on_commit_callbacks(execute=True):
        AppointmentAdmin(Appointment, AdminSite()).save_model(
            _admin_request(staff_user), appointment, form=None, change=True
        )

    appointment.refresh_from_db()
    assert appointment.reminder_sent_at is None
    assert "изменено врачом" in fake_vk.sent(PATIENT_ID)[-1]["message"]

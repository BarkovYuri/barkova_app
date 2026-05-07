from datetime import date, time

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.appointments.models import Appointment
from apps.notifications.models import (
    NotificationLog,
    TelegramPrelink,
    VKPrelink,
)
from apps.scheduling.models import TimeSlot


class PrelinkTokenUniquenessTests(TestCase):
    def test_telegram_prelink_token_unique(self):
        TelegramPrelink.objects.create(token="abc")
        with transaction.atomic(), self.assertRaises(IntegrityError):
            TelegramPrelink.objects.create(token="abc")

    def test_vk_prelink_token_unique(self):
        VKPrelink.objects.create(token="xyz")
        with transaction.atomic(), self.assertRaises(IntegrityError):
            VKPrelink.objects.create(token="xyz")

    def test_prelink_defaults(self):
        link = TelegramPrelink.objects.create(token="t1")
        self.assertFalse(link.is_used)
        self.assertEqual(link.chat_id, "")
        self.assertIsNone(link.linked_at)


class NotificationLogTests(TestCase):
    def setUp(self):
        slot = TimeSlot.objects.create(
            date=date(2026, 6, 1),
            start_time=time(11, 0),
            end_time=time(11, 30),
        )
        self.appointment = Appointment.objects.create(
            slot=slot,
            name="N",
            phone="+79991234567",
            consent_given=True,
            privacy_accepted=True,
            offer_accepted=True,
        )

    def test_create_with_default_pending(self):
        log = NotificationLog.objects.create(
            appointment=self.appointment,
            channel="telegram",
            notification_type="created",
        )
        self.assertEqual(log.status, "pending")
        self.assertEqual(log.payload, {})
        self.assertIsNone(log.sent_at)

    def test_ordering_newest_first(self):
        first = NotificationLog.objects.create(
            appointment=self.appointment,
            channel="telegram",
            notification_type="created",
        )
        second = NotificationLog.objects.create(
            appointment=self.appointment,
            channel="telegram",
            notification_type="reminder_3h",
        )
        ids = list(NotificationLog.objects.values_list("id", flat=True))
        self.assertEqual(ids, [second.id, first.id])

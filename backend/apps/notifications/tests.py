from datetime import date, time

from django.test import TestCase

from apps.appointments.models import Appointment
from apps.notifications.models import NotificationLog
from apps.scheduling.models import TimeSlot


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
            channel="vk",
            notification_type="created",
        )
        self.assertEqual(log.status, "pending")
        self.assertEqual(log.payload, {})
        self.assertIsNone(log.sent_at)

    def test_ordering_newest_first(self):
        first = NotificationLog.objects.create(
            appointment=self.appointment,
            channel="vk",
            notification_type="created",
        )
        second = NotificationLog.objects.create(
            appointment=self.appointment,
            channel="vk",
            notification_type="reminder",
        )
        ids = list(NotificationLog.objects.values_list("id", flat=True))
        self.assertEqual(ids, [second.id, first.id])

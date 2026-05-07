from datetime import date, time

from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.appointments.models import Appointment
from apps.appointments.serializers import (
    AppointmentCreateSerializer,
    _normalize_telegram_username,
    _validate_legal_flags,
)
from apps.scheduling.models import TimeSlot


class LegalFlagsValidatorTests(TestCase):
    def test_all_three_flags_required(self):
        for missing in ("consent_given", "privacy_accepted", "offer_accepted"):
            attrs = {
                "consent_given": True,
                "privacy_accepted": True,
                "offer_accepted": True,
            }
            attrs[missing] = False
            with self.assertRaises(ValidationError) as ctx:
                _validate_legal_flags(attrs)
            self.assertIn(missing, ctx.exception.detail)

    def test_passes_when_all_flags_set(self):
        _validate_legal_flags(
            {"consent_given": True, "privacy_accepted": True, "offer_accepted": True}
        )


class TelegramUsernameNormalizationTests(TestCase):
    def test_strips_at_prefix(self):
        self.assertEqual(_normalize_telegram_username("@alice"), "alice")

    def test_trims_whitespace(self):
        self.assertEqual(_normalize_telegram_username("  bob  "), "bob")

    def test_no_op_for_clean_username(self):
        self.assertEqual(_normalize_telegram_username("carol"), "carol")


class AppointmentCreateSerializerValidationTests(TestCase):
    def test_phone_must_have_at_least_10_digits(self):
        ser = AppointmentCreateSerializer()
        with self.assertRaises(ValidationError):
            ser.validate_phone("+7 999")

    def test_phone_rejects_letters(self):
        ser = AppointmentCreateSerializer()
        with self.assertRaises(ValidationError):
            ser.validate_phone("+7 (999) call-me")

    def test_phone_accepts_formatted(self):
        ser = AppointmentCreateSerializer()
        self.assertEqual(
            ser.validate_phone("+7 (999) 123-45-67"),
            "+7 (999) 123-45-67",
        )

    def test_name_must_be_at_least_two_chars(self):
        ser = AppointmentCreateSerializer()
        with self.assertRaises(ValidationError):
            ser.validate_name("A")

    def test_files_must_have_allowed_extension(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        ser = AppointmentCreateSerializer()
        bad_file = SimpleUploadedFile("evil.exe", b"x")
        with self.assertRaises(ValidationError):
            ser.validate_files([bad_file])

    def test_files_with_no_extension_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        ser = AppointmentCreateSerializer()
        with self.assertRaises(ValidationError):
            ser.validate_files([SimpleUploadedFile("noext", b"x")])


class AppointmentUniqueActiveSlotConstraintTests(TestCase):
    def setUp(self):
        self.slot = TimeSlot.objects.create(
            date=date(2026, 6, 1),
            start_time=time(10, 0),
            end_time=time(10, 30),
        )

    def _make(self, status: str) -> Appointment:
        return Appointment.objects.create(
            slot=self.slot,
            name="A",
            phone="+79991234567",
            consent_given=True,
            privacy_accepted=True,
            offer_accepted=True,
            status=status,
        )

    def test_two_active_appointments_per_slot_blocked(self):
        self._make("new")
        with transaction.atomic(), self.assertRaises(IntegrityError):
            self._make("confirmed")

    def test_cancelled_does_not_block_new(self):
        self._make("cancelled")
        # should be allowed
        self._make("new")
        self.assertEqual(Appointment.objects.filter(slot=self.slot).count(), 2)

    def test_completed_does_not_block_new(self):
        self._make("completed")
        self._make("new")
        self.assertEqual(Appointment.objects.filter(slot=self.slot).count(), 2)

from datetime import date, time

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.scheduling.models import AvailabilityRule, DayException, TimeSlot
from apps.scheduling.reservation import (
    get_reserved_slot_ids,
    is_owned_by,
    is_slot_reserved,
    release_slot,
    reserve_slot,
)
from apps.scheduling.services import generate_slots_for_rule


class AvailabilityRuleTests(TestCase):
    def test_effective_weekdays_prefers_weekdays_array(self):
        rule = AvailabilityRule(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            weekday=2,
            weekdays=[0, 3],
            start_time=time(9, 0),
            end_time=time(18, 0),
        )
        self.assertEqual(rule.effective_weekdays, [0, 3])

    def test_effective_weekdays_falls_back_to_legacy(self):
        rule = AvailabilityRule(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            weekday=4,
            weekdays=[],
            start_time=time(9, 0),
            end_time=time(18, 0),
        )
        self.assertEqual(rule.effective_weekdays, [4])

    def test_effective_weekdays_empty_when_no_data(self):
        rule = AvailabilityRule(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            weekday=None,
            weekdays=[],
            start_time=time(9, 0),
            end_time=time(18, 0),
        )
        self.assertEqual(rule.effective_weekdays, [])


class GenerateSlotsTests(TestCase):
    def test_generates_slots_for_each_matching_weekday(self):
        rule = AvailabilityRule.objects.create(
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 11),
            weekdays=[0, 2],
            start_time=time(10, 0),
            end_time=time(11, 0),
            slot_duration=30,
        )
        created = generate_slots_for_rule(rule)
        self.assertEqual(len(created), 4)
        dates = sorted({slot.date for slot in created})
        self.assertEqual(dates, [date(2026, 1, 5), date(2026, 1, 7)])

    def test_skips_full_day_exceptions(self):
        rule = AvailabilityRule.objects.create(
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 5),
            weekdays=[0],
            start_time=time(9, 0),
            end_time=time(10, 0),
            slot_duration=30,
        )
        DayException.objects.create(date=date(2026, 1, 5), is_full_day=True)
        created = generate_slots_for_rule(rule)
        self.assertEqual(created, [])
        self.assertEqual(TimeSlot.objects.count(), 0)

    def test_idempotent_when_run_twice(self):
        rule = AvailabilityRule.objects.create(
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 5),
            weekdays=[0],
            start_time=time(9, 0),
            end_time=time(10, 0),
            slot_duration=30,
        )
        first = generate_slots_for_rule(rule)
        second = generate_slots_for_rule(rule)
        self.assertEqual(len(first), 2)
        self.assertEqual(second, [])
        self.assertEqual(TimeSlot.objects.count(), 2)

    def test_no_weekdays_returns_empty(self):
        rule = AvailabilityRule.objects.create(
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 11),
            weekdays=[],
            weekday=None,
            start_time=time(10, 0),
            end_time=time(11, 0),
            slot_duration=30,
        )
        self.assertEqual(generate_slots_for_rule(rule), [])


class SlotReservationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.slot = TimeSlot.objects.create(
            date=date(2026, 6, 1),
            start_time=time(10, 0),
            end_time=time(10, 30),
        )

    def test_first_reserve_succeeds(self):
        reservation = reserve_slot(self.slot.id)
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.slot_id, self.slot.id)
        self.assertTrue(reservation.token)
        self.assertTrue(is_slot_reserved(self.slot.id))

    def test_second_reserve_blocked(self):
        first = reserve_slot(self.slot.id)
        second = reserve_slot(self.slot.id)
        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_release_with_correct_token(self):
        reservation = reserve_slot(self.slot.id)
        self.assertTrue(release_slot(self.slot.id, reservation.token))
        self.assertFalse(is_slot_reserved(self.slot.id))

    def test_release_with_wrong_token_does_not_clear(self):
        reservation = reserve_slot(self.slot.id)
        self.assertFalse(release_slot(self.slot.id, "garbage"))
        self.assertTrue(is_slot_reserved(self.slot.id))
        # Owner can still release after a foreign attempt
        self.assertTrue(release_slot(self.slot.id, reservation.token))

    def test_release_with_empty_token_returns_false(self):
        reserve_slot(self.slot.id)
        self.assertFalse(release_slot(self.slot.id, ""))

    def test_is_owned_by_after_release(self):
        reservation = reserve_slot(self.slot.id)
        release_slot(self.slot.id, reservation.token)
        self.assertFalse(is_owned_by(self.slot.id, reservation.token))

    def test_get_reserved_slot_ids_bulk(self):
        other = TimeSlot.objects.create(
            date=date(2026, 6, 1),
            start_time=time(11, 0),
            end_time=time(11, 30),
        )
        third = TimeSlot.objects.create(
            date=date(2026, 6, 1),
            start_time=time(12, 0),
            end_time=time(12, 30),
        )
        reserve_slot(self.slot.id)
        reserve_slot(third.id)
        result = get_reserved_slot_ids([self.slot.id, other.id, third.id])
        self.assertEqual(result, {self.slot.id, third.id})

    def test_get_reserved_slot_ids_empty_input(self):
        self.assertEqual(get_reserved_slot_ids([]), set())


class SlotReserveEndpointTests(TestCase):
    def setUp(self):
        cache.clear()
        self.slot = TimeSlot.objects.create(
            date=date(2026, 6, 1),
            start_time=time(10, 0),
            end_time=time(10, 30),
        )

    def test_reserve_returns_token(self):
        url = reverse("slot-reserve", kwargs={"slot_id": self.slot.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["slot_id"], self.slot.id)
        self.assertTrue(body["reservation_token"])
        self.assertEqual(body["expires_in"], 300)

    def test_reserve_twice_returns_409(self):
        url = reverse("slot-reserve", kwargs={"slot_id": self.slot.id})
        first = self.client.post(url)
        second = self.client.post(url)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)

    def test_reserve_unknown_slot_returns_404(self):
        url = reverse("slot-reserve", kwargs={"slot_id": 99999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_reserve_inactive_slot_returns_404(self):
        self.slot.is_active = False
        self.slot.save(update_fields=["is_active"])
        url = reverse("slot-reserve", kwargs={"slot_id": self.slot.id})
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_reserve_booked_slot_returns_404(self):
        self.slot.is_booked = True
        self.slot.save(update_fields=["is_booked"])
        url = reverse("slot-reserve", kwargs={"slot_id": self.slot.id})
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_release_endpoint_works(self):
        reserve_url = reverse("slot-reserve", kwargs={"slot_id": self.slot.id})
        release_url = reverse("slot-release", kwargs={"slot_id": self.slot.id})

        token = self.client.post(reserve_url).json()["reservation_token"]
        response = self.client.post(
            release_url,
            data={"reservation_token": token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["released"])
        self.assertFalse(is_slot_reserved(self.slot.id))

    def test_release_without_token_400(self):
        url = reverse("slot-release", kwargs={"slot_id": self.slot.id})
        response = self.client.post(url, data={}, content_type="application/json")
        self.assertEqual(response.status_code, 400)

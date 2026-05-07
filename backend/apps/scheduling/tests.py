from datetime import date, time

from django.test import TestCase

from apps.scheduling.models import AvailabilityRule, DayException, TimeSlot
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

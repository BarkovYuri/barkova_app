from rest_framework import serializers

from .models import AvailabilityRule, TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer):
    datetime = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "datetime",
            "is_booked",
            "is_active",
        ]

    def get_datetime(self, obj):
        return f"{obj.date} {obj.start_time.strftime('%H:%M')}"


class AvailabilityRuleSerializer(serializers.ModelSerializer):
    weekday_display = serializers.SerializerMethodField()
    effective_weekdays = serializers.SerializerMethodField()

    class Meta:
        model = AvailabilityRule
        fields = [
            "id",
            "start_date",
            "end_date",
            "weekday",
            "weekdays",
            "effective_weekdays",
            "weekday_display",
            "start_time",
            "end_time",
            "slot_duration",
            "is_active",
        ]

    def get_weekday_display(self, obj):
        from .models import WEEKDAY_SHORT
        days = obj.effective_weekdays
        if not days:
            return "—"
        return ", ".join(WEEKDAY_SHORT[d] for d in sorted(days))

    def get_effective_weekdays(self, obj):
        return obj.effective_weekdays


class GenerateSlotsSerializer(serializers.Serializer):
    rule_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )


class DayToggleSerializer(serializers.Serializer):
    date = serializers.DateField()
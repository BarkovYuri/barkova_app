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
    weekday_display = serializers.CharField(source="get_weekday_display", read_only=True)

    class Meta:
        model = AvailabilityRule
        fields = [
            "id",
            "start_date",
            "end_date",
            "weekday",
            "weekday_display",
            "start_time",
            "end_time",
            "slot_duration",
            "is_active",
        ]


class GenerateSlotsSerializer(serializers.Serializer):
    rule_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )


class DayToggleSerializer(serializers.Serializer):
    date = serializers.DateField()
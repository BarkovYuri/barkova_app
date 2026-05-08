from rest_framework import serializers, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.core.permissions import IsAdminUser

from .models import AvailabilityRule, TimeSlot
from .reservation import (
    RESERVATION_TTL_SECONDS,
    get_reserved_slot_ids,
    release_slot,
    reserve_slot,
)
from .serializers import (
    AvailabilityRuleSerializer,
    DayToggleSerializer,
    GenerateSlotsSerializer,
    TimeSlotSerializer,
)
from .services import (
    close_day_slots,
    generate_slots_for_rules,
    get_available_dates_with_counts,
    get_available_slots_queryset,
    get_date_free_slots_count,
    get_nearest_available_slot,
    open_day_slots,
)


class AvailableDatesView(APIView):

    def get(self, request):
        dates_data = list(get_available_dates_with_counts())
        return Response(dates_data)


class AvailableSlotsView(APIView):

    def get(self, request):
        date = request.query_params.get("date")
        if not date:
            raise serializers.ValidationError({"date": "Параметр date обязателен."})

        raw_slots = TimeSlot.objects.filter(
            date=date,
            is_booked=False,
            is_active=True,
        ).order_by("start_time")

        threshold = timezone.now() + timedelta(hours=1)
        current_tz = timezone.get_current_timezone()

        slots = []
        for slot in raw_slots:
            slot_dt = timezone.make_aware(
                datetime.combine(slot.date, slot.start_time),
                current_tz,
            )
            if slot_dt > threshold:
                slots.append(slot)

        reserved_ids = get_reserved_slot_ids([s.id for s in slots])
        serializer = TimeSlotSerializer(
            slots,
            many=True,
            context={"reserved_slot_ids": reserved_ids},
        )
        return Response(serializer.data)


class SlotReserveView(APIView):
    """Soft-reservation: пользователь выбрал слот, держим за ним 5 минут."""

    throttle_scope = "prelink"

    def post(self, request, slot_id: int):
        slot = get_object_or_404(
            TimeSlot,
            pk=slot_id,
            is_active=True,
            is_booked=False,
        )
        reservation = reserve_slot(slot.id)
        if reservation is None:
            return Response(
                {"detail": "Слот уже зарезервирован другим пользователем."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {
                "slot_id": slot.id,
                "reservation_token": reservation.token,
                "expires_in": RESERVATION_TTL_SECONDS,
            },
            status=status.HTTP_201_CREATED,
        )


class SlotReleaseView(APIView):
    """Освобождает резервирование (например, пользователь поменял слот)."""

    throttle_scope = "prelink"

    def post(self, request, slot_id: int):
        token = (request.data or {}).get("reservation_token", "")
        if not token:
            return Response(
                {"reservation_token": "Токен обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        released = release_slot(slot_id, token)
        return Response({"released": released})


class NearestAvailableSlotView(APIView):

    def get(self, request):
        slot = get_nearest_available_slot()
        if not slot:
            return Response({"detail": "Свободных слотов пока нет."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TimeSlotSerializer(slot)
        return Response(serializer.data)


class DateSummaryView(APIView):

    def get(self, request):
        date = request.query_params.get("date")
        if not date:
            raise serializers.ValidationError({"date": "Параметр date обязателен."})

        free_slots_count = get_date_free_slots_count(date)
        return Response(
            {
                "date": date,
                "free_slots_count": free_slots_count,
                "message": f"Осталось {free_slots_count} свободных мест",
            }
        )


class AdminAvailabilityRuleListView(ListAPIView):
    permission_classes = [IsAdminUser]

    queryset = AvailabilityRule.objects.all().order_by("start_date", "weekday", "start_time")
    serializer_class = AvailabilityRuleSerializer


class AdminGenerateSlotsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = GenerateSlotsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rules = AvailabilityRule.objects.filter(
            id__in=serializer.validated_data["rule_ids"],
            is_active=True,
        )

        created_slots = generate_slots_for_rules(rules)

        return Response(
            {
                "created_count": len(created_slots),
                "created_slot_ids": [slot.id for slot in created_slots],
            },
            status=status.HTTP_201_CREATED,
        )


class AdminCloseDayView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = DayToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_count = close_day_slots(serializer.validated_data["date"])

        return Response(
            {
                "date": serializer.validated_data["date"],
                "closed_slots_count": updated_count,
            }
        )


class AdminOpenDayView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = DayToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_count = open_day_slots(serializer.validated_data["date"])

        return Response(
            {
                "date": serializer.validated_data["date"],
                "opened_slots_count": updated_count,
            }
        )

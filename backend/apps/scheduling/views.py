from datetime import date as date_type
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

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
from .timefmt import msk_offset_hours, slot_start_datetime, timezone_label


def _parse_date_param(request) -> date_type:
    raw = request.query_params.get("date", "")
    try:
        return date_type.fromisoformat(raw)
    except ValueError:
        raise serializers.ValidationError({"date": "Параметр date обязателен в формате ГГГГ-ММ-ДД."}) from None


# Ключи серверного кэша. Инвалидация — через сигнал на TimeSlot
# (см. apps/scheduling/signals.py). TTL небольшой (60 с) на случай если
# сигнал не сработает (например, в bulk_create) — обновление точно
# подтянется максимум через минуту.
_AVAILABLE_DATES_CACHE_KEY = "scheduling:available_dates"
_AVAILABLE_SLOTS_CACHE_KEY_TMPL = "scheduling:available_slots:{date}"
_AVAILABLE_CACHE_TTL = 60


class AvailableDatesView(APIView):

    def get(self, request):
        from django.core.cache import cache as _cache

        cached = _cache.get(_AVAILABLE_DATES_CACHE_KEY)
        if cached is not None:
            return Response(cached)

        dates_data = list(get_available_dates_with_counts())
        _cache.set(_AVAILABLE_DATES_CACHE_KEY, dates_data, timeout=_AVAILABLE_CACHE_TTL)
        return Response(dates_data)


class AvailableSlotsView(APIView):

    def get(self, request):
        from django.core.cache import cache as _cache

        date = _parse_date_param(request)

        # Не кэшируем reserved-флаг (он меняется ежесекундно через
        # Redis-локи), но кэшируем сам список слотов на конкретную
        # дату. Это убирает основной DB-запрос.
        cache_key = _AVAILABLE_SLOTS_CACHE_KEY_TMPL.format(date=date)
        slots_payload = _cache.get(cache_key)

        if slots_payload is None:
            raw_slots = TimeSlot.objects.filter(
                date=date,
                is_booked=False,
                is_active=True,
            ).order_by("start_time")

            threshold = timezone.now() + timedelta(hours=1)
            slots = [slot for slot in raw_slots if slot_start_datetime(slot.date, slot.start_time) > threshold]

            # Сериализуем без is_reserved (он накладывается ниже).
            slots_payload = [dict(item) for item in TimeSlotSerializer(slots, many=True).data]
            _cache.set(cache_key, slots_payload, timeout=_AVAILABLE_CACHE_TTL)

        # is_reserved считаем поверх кэша — он живой из Redis-локов,
        # не зависит от закэшированного списка.
        slot_ids = [s["id"] for s in slots_payload]
        reserved_ids = get_reserved_slot_ids(slot_ids)
        for s in slots_payload:
            s["is_reserved"] = s["id"] in reserved_ids

        return Response(slots_payload)


class ScheduleInfoView(APIView):
    """Часовой пояс расписания — для подписи времени на сайте."""

    def get(self, request):
        return Response(
            {
                "timezone": timezone.get_current_timezone_name(),
                "label": timezone_label(),
                "msk_offset_hours": msk_offset_hours(),
            }
        )


class SlotReserveView(APIView):
    """Soft-reservation: пользователь выбрал слот, держим за ним 5 минут."""

    # Без явного ScopedRateThrottle throttle_scope ничего не ограничивал,
    # и скрипт мог держать все слоты «занятыми».
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "slot_reserve"

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

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "slot_reserve"

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
        date = _parse_date_param(request)

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

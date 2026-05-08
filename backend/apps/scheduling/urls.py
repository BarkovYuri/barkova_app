from django.urls import path

from .views import (
    AdminAvailabilityRuleListView,
    AdminCloseDayView,
    AdminGenerateSlotsView,
    AdminOpenDayView,
    AvailableDatesView,
    AvailableSlotsView,
    DateSummaryView,
    NearestAvailableSlotView,
    SlotReleaseView,
    SlotReserveView,
)

urlpatterns = [
    path("available-dates/", AvailableDatesView.as_view(), name="available-dates"),
    path("available-slots/", AvailableSlotsView.as_view(), name="available-slots"),
    path("nearest-slot/", NearestAvailableSlotView.as_view(), name="nearest-slot"),
    path("date-summary/", DateSummaryView.as_view(), name="date-summary"),
    path("slots/<int:slot_id>/reserve/", SlotReserveView.as_view(), name="slot-reserve"),
    path("slots/<int:slot_id>/release/", SlotReleaseView.as_view(), name="slot-release"),
    path("admin/rules/", AdminAvailabilityRuleListView.as_view(), name="admin-rules"),
    path("admin/generate-slots/", AdminGenerateSlotsView.as_view(), name="admin-generate-slots"),
    path("admin/close-day/", AdminCloseDayView.as_view(), name="admin-close-day"),
    path("admin/open-day/", AdminOpenDayView.as_view(), name="admin-open-day"),
]

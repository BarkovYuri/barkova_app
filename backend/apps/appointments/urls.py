from django.urls import path

from .views import (
    AdminAppointmentListView,
    AdminAppointmentUpdateView,
    AppointmentCreateView,
    VKCallbackView,
    VKMessagingStatusView,
)

urlpatterns = [
    path("", AppointmentCreateView.as_view(), name="appointment-create"),
    path("admin/", AdminAppointmentListView.as_view(), name="admin-appointment-list"),
    path("admin/<int:pk>/", AdminAppointmentUpdateView.as_view(), name="admin-appointment-update"),
    path("vk/messaging-status/", VKMessagingStatusView.as_view(), name="vk-messaging-status"),
    path("vk/callback/", VKCallbackView.as_view(), name="vk-callback"),
]

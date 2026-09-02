from django.urls import path

from .views import (
    AdminAppointmentListView,
    AdminAppointmentUpdateView,
    AppointmentCreateView,
    QuickAppointmentCreateView,
    VKAppointmentActionView,
    VKPrelinkCreateView,
    VKPrelinkLinkView,
    VKPrelinkStatusView,
    VKCallbackView,
    VKMessagingStatusView,
    VKAutoLinkView,
    VKPendingLinkCreateView,
)

urlpatterns = [
    path("", AppointmentCreateView.as_view(), name="appointment-create"),
    path("quick/", QuickAppointmentCreateView.as_view(), name="appointment-quick-create"),
    path("admin/", AdminAppointmentListView.as_view(), name="admin-appointment-list"),
    path("admin/<int:pk>/", AdminAppointmentUpdateView.as_view(), name="admin-appointment-update"),

    path("vk/prelink/", VKPrelinkCreateView.as_view(), name="vk-prelink-create"),
    path("vk/prelink/link/", VKPrelinkLinkView.as_view(), name="vk-prelink-link"),
    path("vk/prelink/status/", VKPrelinkStatusView.as_view(), name="vk-prelink-status"),
    path("vk/messaging-status/", VKMessagingStatusView.as_view(), name="vk-messaging-status"),
    path("vk/action/", VKAppointmentActionView.as_view(), name="vk-appointment-action"),
    path("vk/callback/", VKCallbackView.as_view(), name="vk-callback"),
    path("vk/auto-link/", VKAutoLinkView.as_view(), name="vk-auto-link"),
    path("vk/pending-link/", VKPendingLinkCreateView.as_view(), name="vk-pending-link"),
]

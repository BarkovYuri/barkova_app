from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.content.views import ActiveLegalDocumentListView, SiteBlockListView
from apps.doctors.views import DoctorProfileView

admin.site.site_header = "Кабинет врача"
admin.site.site_title = "Кабинет врача"
admin.site.index_title = "Управление сайтом и записями"

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/profile/", DoctorProfileView.as_view(), name="api-profile"),
    path("api/blocks/", SiteBlockListView.as_view(), name="api-blocks"),
    path("api/legal/", ActiveLegalDocumentListView.as_view(), name="api-legal"),

    path("api/", include("apps.scheduling.urls")),
    path("api/appointments/", include("apps.appointments.urls")),
    path("api/integrations/", include("apps.integrations.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

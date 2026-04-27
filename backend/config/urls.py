from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.doctors.views import DoctorProfileView

admin.site.site_header = "Кабинет врача"
admin.site.site_title = "Кабинет врача"
admin.site.index_title = "Управление сайтом и записями"

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/profile/", DoctorProfileView.as_view(), name="api-profile"),

    # apps.content: /api/blocks/, /api/legal/, /api/services/, /api/how-it-works/,
    # /api/faq/, /api/approach/, /api/trust-badges/
    path("api/", include("apps.content.urls")),

    path("api/", include("apps.scheduling.urls")),
    path("api/appointments/", include("apps.appointments.urls")),
    path("api/integrations/", include("apps.integrations.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

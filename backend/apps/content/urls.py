from django.urls import path
from .views import SiteBlockListView, ActiveLegalDocumentListView

urlpatterns = [
    path("blocks/", SiteBlockListView.as_view(), name="site-blocks"),
    path("legal/", ActiveLegalDocumentListView.as_view(), name="legal-documents"),
]

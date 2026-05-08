from django.urls import path

from .views import (
    ActiveLegalDocumentListView,
    ApproachItemListView,
    ConditionCategoryListView,
    ConsultationFeatureListView,
    FaqItemListView,
    HowItWorksStepListView,
    ServiceListView,
    SiteBlockListView,
    TransportItemListView,
    TrustBadgeListView,
)


urlpatterns = [
    path("blocks/", SiteBlockListView.as_view(), name="site-blocks"),
    path("legal/", ActiveLegalDocumentListView.as_view(), name="legal-documents"),
    path("services/", ServiceListView.as_view(), name="services"),
    path(
        "how-it-works/",
        HowItWorksStepListView.as_view(),
        name="how-it-works-steps",
    ),
    path("faq/", FaqItemListView.as_view(), name="faq-items"),
    path("approach/", ApproachItemListView.as_view(), name="approach-items"),
    path("trust-badges/", TrustBadgeListView.as_view(), name="trust-badges"),
    path("transport/", TransportItemListView.as_view(), name="transport-items"),
    path(
        "consultation-features/",
        ConsultationFeatureListView.as_view(),
        name="consultation-features",
    ),
    path("conditions/", ConditionCategoryListView.as_view(), name="conditions"),
]

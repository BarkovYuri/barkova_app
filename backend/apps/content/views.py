from rest_framework.generics import ListAPIView
from .models import SiteBlock, LegalDocument
from .serializers import SiteBlockSerializer, LegalDocumentSerializer


class SiteBlockListView(ListAPIView):
    queryset = SiteBlock.objects.all().order_by("id")
    serializer_class = SiteBlockSerializer


class ActiveLegalDocumentListView(ListAPIView):
    serializer_class = LegalDocumentSerializer

    def get_queryset(self):
        return LegalDocument.objects.filter(is_active=True).order_by("doc_type", "-created_at")

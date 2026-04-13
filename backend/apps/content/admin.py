from django.contrib import admin
from .models import SiteBlock, LegalDocument


@admin.register(SiteBlock)
class SiteBlockAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "updated_at")
    search_fields = ("key", "title")


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "doc_type", "version", "is_active", "created_at")
    list_filter = ("doc_type", "is_active")
    search_fields = ("title", "version")
from __future__ import annotations

from django.contrib import admin

from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


@admin.register(EntryVersionBlock)
class EntryVersionBlockAdmin(admin.ModelAdmin):
    list_display = ['version__entry__name', 'type', '_block_data', 'is_deleted']
    list_select_related = ['version__entry']
    list_filter = ['type', 'is_deleted', 'is_active']
    search_fields = ['version__entry__name']
    ordering = ['-created_datetime']
    autocomplete_fields = ['version']

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.knowledge.entry.models import Entry

if TYPE_CHECKING:
    from django.db.models import QuerySet


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_version_link', 'collection', 'is_deleted', 'tag_count']
    list_select_related = ['collection', 'current_version']
    list_filter = ['is_deleted', 'is_active']
    search_fields = ['name', 'collection__name']
    ordering = ['name']
    autocomplete_fields = ['collection', 'current_version']
    actions = ['set_tags_for_entries']

    def current_version_link(self, entry: Entry) -> str:
        url = (
            reverse('admin:django_spire_knowledge_entryversion_changelist')
            + '?'
            + urlencode({'entry_id': f'{entry.id}'})
        )

        return format_html(f'<a href="{url}">View Versions</a>')

    current_version_link.short_description = 'Current Version'
    current_version_link.allow_tags = True

    @admin.action(description="Set Tags for Entries (Allow 5 Seconds Per)")
    def set_tags_for_entries(self, request, queryset: QuerySet[Entry]):
        processed = 0
        for entry in queryset:
            entry.services.tag.process_and_set_tags()
            processed += 1

        messages.success(request, f'Successfully processed {processed} entries.')

    def tag_count(self, entry: Entry):
        return entry.tags.count()

    tag_count.short_description = 'Tags'

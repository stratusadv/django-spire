from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html

from django_spire.contrib.admin.links import admin_changelist_url
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


TAG_ACTION_MAX_ROWS = 25


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    actions = ('set_tags_for_entries',)
    autocomplete_fields = ('collection', 'current_version')

    list_display = ('name', 'current_version_link', 'collection', 'is_deleted', 'tag_count')
    list_filter = ('is_deleted', 'is_active')
    list_select_related = ('collection', 'current_version')
    ordering = ('name',)
    search_fields = ('name', 'collection__name')

    @admin.display(description='Current Version')
    def current_version_link(self, entry: Entry) -> str:
        url = admin_changelist_url(EntryVersion, entry_id=str(entry.id))

        return format_html('<a href="{}">View Versions</a>', url)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Entry]:
        queryset = super().get_queryset(request)

        return queryset.annotate(_tag_count=Count('tags', distinct=True))

    @admin.action(description='Set Tags for Entries (Allow 5 Seconds Per)')
    def set_tags_for_entries(self, request: HttpRequest, queryset: QuerySet[Entry]) -> None:
        if queryset.count() > TAG_ACTION_MAX_ROWS:
            message = (
                f'Select at most {TAG_ACTION_MAX_ROWS} entries at a time. '
                f'Tagging runs inline and will time out on larger selections.'
            )

            messages.error(request, message)
            return

        processed = 0

        for entry in queryset:
            entry.services.tag.process_and_set_tags()
            processed += 1

        messages.success(request, f'Successfully processed {processed} entries.')

    @admin.display(description='Tags', ordering='_tag_count')
    def tag_count(self, entry: Entry) -> int:
        return entry._tag_count

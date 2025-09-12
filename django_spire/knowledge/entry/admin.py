from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.knowledge.entry.models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_version_link', 'collection', 'is_deleted']
    list_select_related = ['collection', 'current_version']
    list_filter = ['is_deleted', 'is_active']
    search_fields = ['name', 'collection__name']
    ordering = ['name']
    autocomplete_fields = ['collection', 'current_version']

    def current_version_link(self, entry: Entry) -> str:
        url = (
            reverse('admin:django_spire_knowledge_entryversion_changelist')
            + '?'
            + urlencode({'entry_id': f'{entry.id}'})
        )

        return format_html(f'<a href="{url}">View Versions</a>')

    current_version_link.short_description = 'Current Version'
    current_version_link.allow_tags = True

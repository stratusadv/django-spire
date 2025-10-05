from __future__ import annotations

from django.contrib import admin

from django_spire.knowledge.entry.version.models import EntryVersion


@admin.register(EntryVersion)
class EntryVersionAdmin(admin.ModelAdmin):
    list_display = [
        'entry__name', 'entry__collection', 'author', 'last_edit_datetime',
        'published_datetime', 'is_deleted'
    ]
    list_select_related = ['entry__collection', 'author']
    list_filter = ['status', 'is_deleted', 'is_active']
    search_fields = ['entry__name', 'author__first_name', 'author__last_name']
    ordering = ['-last_edit_datetime']
    autocomplete_fields = ['entry', 'author']

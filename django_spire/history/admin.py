from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.history import models


@admin.register(models.HistoryEvent)
class HistoryEventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'content_object_link', 'content_type', 'created_datetime', 'event_verbose'
    )
    list_filter = ('event', 'created_datetime')
    search_fields = ('id', 'content_type__model',)
    ordering = ('-created_datetime',)

    def content_object_link(self, history_event: models.HistoryEvent) -> str:
        url = reverse(
            f'admin:{history_event.content_type.app_label}_{history_event.content_type.model}_change',
            args=[history_event.object_id]
        )

        return format_html(f'<a href="{url}">{history_event.content_object}</a>')

    content_object_link.short_description = 'Content Object'

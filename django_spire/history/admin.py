from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin

from django_spire.contrib.admin.links import admin_change_link
from django_spire.history import models

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(models.HistoryEvent)
class HistoryEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'content_object_link',
        'content_type',
        'created_datetime',
        'event_verbose',
    )
    list_filter = ('event', 'created_datetime')
    list_select_related = ('content_type',)
    ordering = ('-created_datetime',)
    search_fields = ('id', 'content_type__model')

    @admin.display(description='Content Object')
    def content_object_link(self, history_event: models.HistoryEvent) -> str:
        return admin_change_link(history_event.content_object, empty_text='No Related Object')

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.HistoryEvent]:
        queryset = super().get_queryset(request)

        return queryset.prefetch_related('content_object')

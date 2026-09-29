from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from celery import states
from django.contrib import admin

from django_spire.celery import models

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class CeleryTaskStateFilter(admin.SimpleListFilter):
    title = 'state'
    parameter_name = 'state'

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[str, str]]:
        standard_states = list(states.ALL_STATES)
        observed_states = model_admin.model.objects.values_list('state', flat=True).distinct()

        return [
            (state, state.replace('_', ' ').title())
            for state in dict.fromkeys([*standard_states, *observed_states])
        ]

    def queryset(
        self, request: HttpRequest, queryset: QuerySet[models.CeleryTask]
    ) -> QuerySet[models.CeleryTask]:
        if self.value():
            return queryset.filter(state=self.value())

        return queryset


@admin.register(models.CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'state_display', 'started_datetime', 'task_name')
    list_filter = (
        'task_name',
        'display_name',
        CeleryTaskStateFilter,
        'started_datetime',
        'completed_datetime',
    )
    ordering = ('-started_datetime',)
    search_fields = (
        'task_name',
        'display_name',
        'state',
        'reference_key',
        'started_datetime',
        'completed_datetime',
    )

    readonly_fields = (
        'task_id',
        'reference_key',
        'model_key',
        'task_name',
        'display_name',
        'state_display',
        'queued_datetime',
        'started_datetime',
        'completed_datetime',
        '_task_meta',
        'result_verbose',
    )
    fields = (
        'task_id',
        'reference_key',
        'model_key',
        'task_name',
        'display_name',
        'state_display',
        'queued_datetime',
        'started_datetime',
        'completed_datetime',
        '_task_meta',
        'result_verbose',
    )

    @admin.display(description='State', ordering='state')
    def state_display(self, obj: models.CeleryTask) -> str:
        return obj.state.replace('_', ' ').title()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

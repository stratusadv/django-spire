from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from celery import states
from django import forms
from django.contrib import admin, messages

from django_spire.celery import models
from django_spire.contrib.form.widgets import JsonTreeWidget

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


class CeleryTaskModelForm(forms.ModelForm):
    _task_meta = forms.JSONField(widget=JsonTreeWidget, required=False)

    class Meta:
        model = models.CeleryTask
        fields = ('_task_meta',)


@admin.register(models.CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    form = CeleryTaskModelForm
    actions = ('cancel_selected_celery_tasks',)

    list_display = ('display_name', 'state_display', 'queued_datetime', 'task_name')
    list_filter = (
        'task_name',
        'display_name',
        CeleryTaskStateFilter,
        'queued_datetime',
        'completed_datetime',
    )
    ordering = ('-queued_datetime',)
    search_fields = (
        'task_name',
        'display_name',
        'state',
        'reference_key',
        'queued_datetime',
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
        'result_verbose',
        'exception_result',
        'exception_traceback',
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
        'exception_result',
        'exception_traceback',
    )

    @admin.display(description='State', ordering='state')
    def state_display(self, obj: models.CeleryTask) -> str:
        return obj.state.replace('_', ' ').title()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @admin.action(description='Cancel Selected Celery Tasks', permissions=('change',))
    def cancel_selected_celery_tasks(self, request: HttpRequest, queryset: QuerySet) -> None:
        canceled_count = 0

        for celery_task in queryset:
            error = celery_task.services.cancel()

            if error is None:
                canceled_count += 1
            else:
                messages.warning(request, f'{celery_task.display_name}: {error}')

        messages.success(request, f'Canceled {canceled_count} Celery Task(s)')

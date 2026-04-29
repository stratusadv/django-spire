from django.contrib import admin

from django_spire.celery import models


@admin.register(models.CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    list_display = (
        'task_name',
        'display_name',
        'state',
        'started_datetime',
        'estimated_completion_datetime',
        'completed_datetime',
    )
    list_filter = ('task_name', 'display_name', 'state', 'started_datetime', 'completed_datetime')
    search_fields = ('task_name', 'display_name', 'state', 'started_datetime', 'completed_datetime')
    ordering = ('-started_datetime',)

    readonly_fields = [
        'task_id',
        'reference_key',
        'model_key',
        'task_name',
        'display_name',
        'state',
        'started_datetime',
        'estimated_completion_datetime',
        'completed_datetime',
    ]
    fields = [
        'task_id',
        'reference_key',
        'model_key',
        'task_name',
        'display_name',
        'state',
        'started_datetime',
        'estimated_completion_datetime',
        'completed_datetime',
    ]
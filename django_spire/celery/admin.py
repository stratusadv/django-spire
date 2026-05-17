from django.contrib import admin

from django_spire.celery import models


@admin.register(models.CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'state',
        'started_datetime',
        'completed_datetime',
        'reference_key',
        'task_name',
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
        'completed_datetime',
        '_task_meta',
        '_result'
    ]
    fields = [
        'task_id',
        'reference_key',
        'model_key',
        'task_name',
        'display_name',
        'state',
        'started_datetime',
        'completed_datetime',
        '_task_meta',
        '_result'
    ]
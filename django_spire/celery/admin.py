from django.contrib import admin

from django_spire.celery import models


@admin.register(models.CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    list_display = (
        'app_name',
        'reference_name',
        'state',
        'started_datetime',
        'estimated_completion_datetime',
        'completed_datetime',
    )
    list_filter = ('app_name', 'reference_name', 'state', 'started_datetime', 'completed_datetime')
    search_fields = ('app_name', 'reference_name', 'state', 'started_datetime', 'completed_datetime')
    ordering = ('-started_datetime',)

    readonly_fields = [
        'task_id',
        'reference_key',
        'app_name',
        'reference_name',
        'state',
        'started_datetime',
        'estimated_completion_datetime',
        'completed_datetime',
    ]
    fields = [
        'task_id',
        'reference_key',
        'app_name',
        'reference_name',
        'state',
        'started_datetime',
        'estimated_completion_datetime',
        'completed_datetime',
    ]

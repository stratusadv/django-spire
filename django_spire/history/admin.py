from django.contrib import admin
from django_spire.history import models


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'content_type', 'created_datetime', 'verb', 'user')
    list_filter = ('verb',)
    search_fields = ('id', 'actor__first_name', 'user__first_name', 'content_type__model')

    class Meta:
        ordering = ('created_datetime',)


admin.site.register(models.ActivityLog, ActivityLogAdmin)


class EventHistoryAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'created_datetime', 'event_verbose')
    list_filter = ('event',)
    search_fields = ('id', 'content_type__model',)

    class Meta:
        ordering = ('created_datetime',)


admin.site.register(models.EventHistory, EventHistoryAdmin)


class ViewAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'created_datetime', 'user')

    class Meta:
        ordering = ('created_datetime',)


admin.site.register(models.View, ViewAdmin)

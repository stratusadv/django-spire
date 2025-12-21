from __future__ import annotations

from django.contrib import admin

from django_spire.notification.push.models import PushNotification


@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_datetime', 'is_active', 'is_deleted')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('-created_datetime',)

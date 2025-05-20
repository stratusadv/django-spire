from django.contrib import admin

from django_spire.notification.app.models import AppNotification


@admin.register(AppNotification)
class AppNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'notification', 'created_datetime', 'is_deleted'
    )

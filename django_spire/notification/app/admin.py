from django.contrib import admin

from django_spire.notification.app.models import AppNotification

# Register your models here.
@admin.register(AppNotification)
class AppNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'notification', 'user'
    )

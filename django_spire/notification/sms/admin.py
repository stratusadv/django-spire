from django.contrib import admin

from django_spire.notification.sms.models import SmsNotification


@admin.register(SmsNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'notification', 'to_phone_number'
    )

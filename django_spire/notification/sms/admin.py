from django.contrib import admin

from django_spire.notification.sms.models import SmsNotification, SmsTemporaryMedia


@admin.register(SmsNotification)
class SmsNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'notification', 'to_phone_number'
    )


@admin.register(SmsTemporaryMedia)
class SmsTemporaryMediaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'content_type', 'external_url'
    )

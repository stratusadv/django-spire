from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.notification.sms.models import SmsNotification, SmsTemporaryMedia


@admin.register(SmsNotification)
class SmsNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'view_notification_link', 'to_phone_number', 'media_url', 'temporary_media'
    )
    list_filter = (
        ('temporary_media', admin.EmptyFieldListFilter),
        ('media_url', admin.EmptyFieldListFilter),
    )
    list_select_related = ('notification', )

    def view_notification_link(self, sms_notification: SmsNotification):
        url = (
                reverse("admin:django_spire_notification_notification_changelist")
                + "?"
                + urlencode({"id": f"{sms_notification.notification_id}"})
        )

        return format_html(f'<a href="{url}">{sms_notification.notification}</a>')

    view_notification_link.short_description = "Notification"


@admin.register(SmsTemporaryMedia)
class SmsTemporaryMediaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'content_type', 'external_url'
    )

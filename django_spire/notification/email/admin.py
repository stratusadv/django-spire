from __future__ import annotations

from django.contrib import admin

from django_spire.notification.email.models import EmailNotification


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification', 'to_recipients')
    list_select_related = ('notification',)
    readonly_fields = ('to_email_address',)
    search_fields = ('id', 'to', 'to_email_address')

    @admin.display(description='To')
    def to_recipients(self, email_notification: EmailNotification) -> str:
        return ', '.join(email_notification.to)

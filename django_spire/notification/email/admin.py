from __future__ import annotations

from django.contrib import admin

from django_spire.notification.email.models import EmailNotification


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification', 'to_email_address')
    list_select_related = ('notification',)
    search_fields = ('id', 'to_email_address')

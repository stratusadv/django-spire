from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from django_spire.notification import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'type', 'user', 'view_body_snippet', 'url_link', 'status',
        'status_message', 'priority', 'sent_datetime', 'publish_datetime',
        'content_type', 'object_id', 'is_deleted'
    )
    list_filter = ('type',)
    search_fields = ('id', 'title', 'type')

    def view_body_snippet(self, notification: models.Notification) -> str:
        return (
            notification.body[:20] + '...'
            if len(notification.body) > 20
            else notification.body
        )

    view_body_snippet.short_description = 'Body Snippet'

    def url_link(self, notification: models.Notification) -> str:
        if notification.url:
            return format_html(f'<a href="{notification.url}" target="_blank">Link</a>')

        return 'No URL'

    url_link.short_description = 'Notification URL'

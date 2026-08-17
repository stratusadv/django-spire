from __future__ import annotations

from django.contrib import admin

from django_spire.contrib.admin.links import external_link
from django_spire.notification import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'type',
        'user',
        'view_body_snippet',
        'url_link',
        'status',
        'status_message',
        'priority',
        'sent_datetime',
        'publish_datetime',
        'content_type',
        'object_id',
        'is_deleted',
    )
    list_filter = ('type',)
    list_select_related = ('user', 'content_type')
    search_fields = ('id', 'title', 'type')

    @admin.display(description='Notification URL')
    def url_link(self, notification: models.Notification) -> str:
        return external_link(notification.url, 'Link', empty_text='No URL')

    @admin.display(description='Body Snippet')
    def view_body_snippet(self, notification: models.Notification) -> str:
        if len(notification.body) > 20:
            return notification.body[:20] + '...'

        return notification.body

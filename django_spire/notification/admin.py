from django.contrib import admin
from django.utils.html import format_html

from django_spire.notification import models

@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'type', 'is_processed', 'processed_datetime',
        'processed_datetime', 'view_body_snippet', 'url_link',
        'content_type', 'object_id'
    )
    list_filter = ('type', 'is_processed', 'processed_datetime')
    search_fields = ('id', 'title', 'type')
    ordering = ('-processed_datetime',)

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

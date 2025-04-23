from django.contrib import admin
from django.urls.base import reverse
from django.utils.html import format_html

from django_spire.history.activity.models import Activity


@admin.register(Activity)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'content_object_link', 'content_type', 'created_datetime',
        'verb', 'user_link', 'recipient_link', 'information_snippet'
    )
    list_filter = ('verb', 'created_datetime')
    search_fields = ('id', 'user__first_name', 'user__last_name', 'recipient__first_name', 'recipient__last_name', 'content_type__model', 'verb')
    ordering = ('-created_datetime',)

    def content_object_link(self, activity: Activity) -> str:
        url = reverse(
            f'admin:{activity.content_type.app_label}_{activity.content_type.model}_change',
            args=[activity.object_id]
        )

        return format_html(f'<a href="{url}">{activity.content_object}</a>')

    content_object_link.short_description = 'Content Object'

    def user_link(self, activity: Activity) -> str:
        url = reverse('admin:auth_user_change', args=[activity.user.id])
        return format_html(f'<a href="{url}">{activity.user.get_full_name()}</a>')

    user_link.short_description = 'User'

    def recipient_link(self, activity: Activity) -> str:
        if activity.recipient:
            url = reverse('admin:auth_user_change', args=[activity.recipient.id])
            return format_html(f'<a href="{url}">{activity.recipient.get_full_name()}</a>')

        return 'No Recipient'

    recipient_link.short_description = 'Recipient'

    def information_snippet(self, activity: Activity) -> str:
        return (
            activity.information[:20] + '...'
            if activity.information and len(activity.information) > 20
            else activity.information or 'No Information'
        )

    information_snippet.short_description = 'Information Snippet'

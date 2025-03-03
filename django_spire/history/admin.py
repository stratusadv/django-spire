from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.history import models
from django_spire.history.activity.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'content_object_link', 'content_type', 'created_datetime',
        'verb', 'user_link', 'recipient_link', 'information_snippet'
    )
    list_filter = ('verb', 'created_datetime')
    search_fields = ('id', 'user__first_name', 'user__last_name', 'recipient__first_name', 'recipient__last_name', 'content_type__model', 'verb')
    ordering = ('-created_datetime',)

    def content_object_link(self, activity: ActivityLog) -> str:
        url = reverse(
            f'admin:{activity.content_type.app_label}_{activity.content_type.model}_change',
            args=[activity.object_id]
        )

        return format_html(f'<a href="{url}">{activity.content_object}</a>')

    content_object_link.short_description = 'Content Object'

    def user_link(self, activity: ActivityLog) -> str:
        url = reverse('admin:auth_user_change', args=[activity.user.id])
        return format_html(f'<a href="{url}">{activity.user.get_full_name()}</a>')

    user_link.short_description = 'User'

    def recipient_link(self, activity: ActivityLog) -> str:
        if activity.recipient:
            url = reverse('admin:auth_user_change', args=[activity.recipient.id])
            return format_html(f'<a href="{url}">{activity.recipient.get_full_name()}</a>')

        return 'No Recipient'

    recipient_link.short_description = 'Recipient'

    def information_snippet(self, activity: ActivityLog) -> str:
        return (
            activity.information[:20] + '...'
            if activity.information and len(activity.information) > 20
            else activity.information or 'No Information'
        )

    information_snippet.short_description = 'Information Snippet'


@admin.register(models.EventHistory)
class EventHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'content_object_link', 'content_type', 'created_datetime', 'event_verbose'
    )
    list_filter = ('event', 'created_datetime')
    search_fields = ('id', 'content_type__model',)
    ordering = ('-created_datetime',)

    def content_object_link(self, event_history: models.EventHistory) -> str:
        url = reverse(
            f'admin:{event_history.content_type.app_label}_{event_history.content_type.model}_change',
            args=[event_history.object_id]
        )

        return format_html(f'<a href="{url}">{event_history.content_object}</a>')

    content_object_link.short_description = 'Content Object'


@admin.register(models.View)
class ViewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'content_object_link', 'user_link', 'created_datetime'
    )
    list_filter = ('created_datetime',)
    search_fields = ('id', 'user__first_name', 'user__last_name', 'content_type__model',)
    ordering = ('-created_datetime',)

    def content_object_link(self, view: models.View) -> str:
        url = reverse(
            f'admin:{view.content_type.app_label}_{view.content_type.model}_change',
            args=[view.object_id]
        )

        return format_html(f'<a href="{url}">{view.content_object}</a>')

    content_object_link.short_description = 'Content Object'

    def user_link(self, view: models.View) -> str:
        url = reverse('admin:auth_user_change', args=[view.user.id])
        return format_html(f'<a href="{url}">{view.user.get_full_name()}</a>')

    user_link.short_description = 'User'

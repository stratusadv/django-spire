from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin

from django_spire.contrib.admin.links import admin_change_link
from django_spire.history.activity.models import Activity

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'content_object_link',
        'content_type',
        'created_datetime',
        'verb',
        'user_link',
        'recipient_link',
        'information_snippet',
    )
    list_filter = ('verb', 'created_datetime')
    list_select_related = ('content_type', 'user', 'recipient')
    ordering = ('-created_datetime',)
    search_fields = (
        'id',
        'user__first_name',
        'user__last_name',
        'recipient__first_name',
        'recipient__last_name',
        'content_type__model',
        'verb',
    )

    @admin.display(description='Content Object')
    def content_object_link(self, activity: Activity) -> str:
        return admin_change_link(activity.content_object, empty_text='No Related Object')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Activity]:
        queryset = super().get_queryset(request)

        return queryset.prefetch_related('content_object')

    @admin.display(description='Information Snippet')
    def information_snippet(self, activity: Activity) -> str:
        if not activity.information:
            return 'No Information'

        if len(activity.information) > 20:
            return activity.information[:20] + '...'

        return activity.information

    @admin.display(description='Recipient')
    def recipient_link(self, activity: Activity) -> str:
        return admin_change_link(activity.recipient, empty_text='No Recipient')

    @admin.display(description='User')
    def user_link(self, activity: Activity) -> str:
        return admin_change_link(activity.user)

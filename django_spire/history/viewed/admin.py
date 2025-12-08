from __future__ import annotations

from django.contrib import admin
from django.urls.base import reverse
from django.utils.html import format_html

from django_spire.history.viewed.models import Viewed


@admin.register(Viewed)
class ViewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'content_object_link', 'user_link', 'created_datetime'
    )
    list_filter = ('created_datetime',)
    search_fields = ('id', 'user__first_name', 'user__last_name', 'content_type__model',)
    ordering = ('-created_datetime',)

    def content_object_link(self, view: Viewed) -> str:
        url = reverse(
            f'admin:{view.content_type.app_label}_{view.content_type.model}_change',
            args=[view.object_id]
        )

        return format_html(f'<a href="{url}">{view.content_object}</a>')

    content_object_link.short_description = 'Content Object'

    def user_link(self, view: Viewed) -> str:
        url = reverse('admin:auth_user_change', args=[view.user.id])
        return format_html(f'<a href="{url}">{view.user.get_full_name()}</a>')

    user_link.short_description = 'User'

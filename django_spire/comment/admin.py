from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.comment import models


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_link', 'content_object_link', 'information_snippet',
        'created_datetime', 'is_edited'
    )
    list_filter = ('created_datetime', 'is_edited')
    search_fields = ('id', 'user__username', 'information')
    ordering = ('-created_datetime',)

    def user_link(self, comment: models.Comment) -> str:
        url = reverse('admin:auth_user_change', args=[comment.user.id])
        return format_html(f'<a href="{url}">{comment.user.username}</a>')

    user_link.short_description = 'User'

    def content_object_link(self, comment: models.Comment) -> str:
        url = (
            reverse(
                f'admin:{comment.content_type.app_label}_{comment.content_type.model}_change',
                args=[comment.object_id]
            )
        )

        return format_html(f'<a href="{url}">{comment.content_object}</a>')

    content_object_link.short_description = 'Content Object'

    def information_snippet(self, comment: models.Comment) -> str:
        return (
            comment.information[:20] + '...'
            if len(comment.information) > 20
            else comment.information
        )

    information_snippet.short_description = 'Comment Snippet'

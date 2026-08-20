from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin

from django_spire.comment import models
from django_spire.contrib.admin.links import admin_change_link

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_link',
        'content_object_link',
        'information_snippet',
        'created_datetime',
        'is_edited',
    )
    list_filter = ('created_datetime', 'is_edited')
    list_select_related = ('user', 'content_type')
    ordering = ('-created_datetime',)
    search_fields = ('id', 'user__username', 'information')

    @admin.display(description='Content Object')
    def content_object_link(self, comment: models.Comment) -> str:
        return admin_change_link(comment.content_object, empty_text='No Related Object')

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Comment]:
        queryset = super().get_queryset(request)

        return queryset.prefetch_related('content_object')

    @admin.display(description='Comment Snippet')
    def information_snippet(self, comment: models.Comment) -> str:
        if len(comment.information) > 20:
            return comment.information[:20] + '...'

        return comment.information

    @admin.display(description='User')
    def user_link(self, comment: models.Comment) -> str:
        return admin_change_link(comment.user)

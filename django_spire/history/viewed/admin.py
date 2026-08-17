from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin

from django_spire.contrib.admin.links import admin_change_link
from django_spire.history.viewed.models import Viewed

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(Viewed)
class ViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object_link', 'user_link', 'created_datetime')
    list_filter = ('created_datetime',)
    list_select_related = ('content_type', 'user')
    ordering = ('-created_datetime',)
    search_fields = ('id', 'user__first_name', 'user__last_name', 'content_type__model')

    @admin.display(description='Content Object')
    def content_object_link(self, view: Viewed) -> str:
        return admin_change_link(view.content_object, empty_text='No Related Object')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Viewed]:
        queryset = super().get_queryset(request)

        return queryset.prefetch_related('content_object')

    @admin.display(description='User')
    def user_link(self, view: Viewed) -> str:
        return admin_change_link(view.user)

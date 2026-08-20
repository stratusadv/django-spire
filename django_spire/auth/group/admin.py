from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from django_spire.auth.group import models

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(models.AuthGroup)
class PortalGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'view_group_detail_link', 'user_count')
    ordering = ('name',)
    search_fields = ('id', 'name')

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.AuthGroup]:
        queryset = super().get_queryset(request)

        return queryset.annotate(_user_count=Count('user', distinct=True))

    @admin.display(description='User Count', ordering='_user_count')
    def user_count(self, group: models.AuthGroup) -> int:
        return group._user_count

    @admin.display(description='Details Link')
    def view_group_detail_link(self, group: models.AuthGroup) -> str:
        url = reverse('django_spire:auth:group:page:detail', kwargs={'pk': group.pk})

        return format_html('<a href="{}">View Details</a>', url)

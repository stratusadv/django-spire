from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin
from django.utils.html import format_html

from django_spire.contrib.admin.links import admin_change_link
from django_spire.file import models

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'formatted_size', 'content_object_link', 'file_link')
    list_filter = ('type',)
    list_select_related = ('content_type',)
    ordering = ('-id',)
    search_fields = ('id', 'name', 'type')

    @admin.display(description='Content Object')
    def content_object_link(self, file: models.File) -> str:
        return admin_change_link(file.content_object, empty_text='No Related Object')

    @admin.display(description='File Download Link')
    def file_link(self, file: models.File) -> str:
        if not file.file:
            return 'No File'

        return format_html('<a href="{}" download>{}</a>', file.file.url, file.name)

    @admin.display(description='Size')
    def formatted_size(self, file: models.File) -> str:
        return file.formatted_size

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.File]:
        queryset = super().get_queryset(request)

        return queryset.prefetch_related('content_object')

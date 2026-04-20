from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.file import models


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'type', 'formatted_size', 'content_object_link', 'file_link'
    )
    list_filter = ('type',)
    search_fields = ('id', 'name', 'type')
    ordering = ('-id',)

    def formatted_size(self, file: models.File) -> str:
        return file.formatted_size

    formatted_size.short_description = 'Size'

    def content_object_link(self, file: models.File) -> str:
        if file.content_type is None or file.object_id is None:
            return 'No Related Object'

        content_object = file.content_object

        if content_object is None:
            return 'No Related Object'

        url = reverse(
            f'admin:{file.content_type.app_label}_{file.content_type.model}_change',
            args=[file.object_id]
        )

        return format_html('<a href="{}">{}</a>', url, content_object)

    content_object_link.short_description = 'Content Object'

    def file_link(self, file: models.File) -> str:
        return format_html('<a href="{}" download>{}</a>', file.file.url, file.name)

    file_link.short_description = 'File Download Link'

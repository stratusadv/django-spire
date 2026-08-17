from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin

from django_spire.api.models import ApiAccess

if TYPE_CHECKING:
    from django.http import HttpRequest


@admin.register(ApiAccess)
class ApiAccessAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission', 'key_hint', 'created_datetime')
    list_filter = ('permission',)
    readonly_fields = ('hashed_key', 'key_hint', 'created_datetime')
    search_fields = ('name', 'key_hint')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin

from django_spire.api.models import ApiAccess

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest


@admin.register(ApiAccess)
class ApiAccessAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission', 'has_super_access', 'key_hint', 'created_datetime')
    list_filter = ('permission',)
    readonly_fields = ('hashed_key', 'key_hint', 'created_datetime')
    search_fields = ('name', 'key_hint')

    def get_readonly_fields(self, request: HttpRequest, obj: Model | None = None) -> list[str]:
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if not request.user.is_superuser:
            readonly_fields.append('has_super_access')

        return readonly_fields

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

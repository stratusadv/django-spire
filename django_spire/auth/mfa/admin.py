from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin

from django_spire.auth.mfa import models
from django_spire.contrib.admin.links import admin_change_link

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest


@admin.register(models.MfaCode)
class MfaCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'expiration_datetime', 'is_code_valid')
    list_filter = ('expiration_datetime',)
    list_select_related = ('user',)
    ordering = ('-expiration_datetime',)
    search_fields = ('id', 'user__username')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return False

    @admin.display(boolean=True, description='Valid')
    def is_code_valid(self, mfa_code: models.MfaCode) -> bool:
        return mfa_code.is_valid()

    @admin.display(description='User')
    def user_link(self, mfa_code: models.MfaCode) -> str:
        return admin_change_link(mfa_code.user)

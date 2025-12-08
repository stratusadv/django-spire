from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.auth.mfa import models


@admin.register(models.MfaCode)
class MfaCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_link', 'code', 'expiration_datetime', 'is_valid'
    )
    list_filter = ('expiration_datetime',)
    search_fields = ('id', 'user__username', 'code')
    ordering = ('-expiration_datetime',)

    def user_link(self, mfa_code: models.MfaCode) -> str:
        url = reverse('admin:auth_user_change', args=[mfa_code.user.id])
        return format_html(f'<a href="{url}">{mfa_code.user.username}</a>')

    user_link.short_description = 'User'

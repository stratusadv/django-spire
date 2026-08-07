from __future__ import annotations

from django.contrib import admin

from django_spire.auth.sms.models import SmsAuth


@admin.register(SmsAuth)
class SmsAuthAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'is_verified', 'verified_datetime')
    list_filter = ('is_verified',)
    search_fields = ('phone_number', 'user__username', 'user__email')
    readonly_fields = (
        'code_attempt_count',
        'code_expiration_datetime',
        'code_hash',
        'code_purpose',
        'created_datetime',
        'session_last_activity_datetime',
        'session_started_datetime',
        'verified_datetime',
    )

    class Meta:
        ordering = ('phone_number',)

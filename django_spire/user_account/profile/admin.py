from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.user_account.profile import models


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_link', 'username', 'mfa_status', 'mfa_valid_till_datetime'
    )
    list_filter = ('mfa_valid_till_datetime',)
    search_fields = ('id', 'user__username', 'user__email')
    ordering = ('user__username',)

    def user_link(self, profile: models.UserProfile) -> str:
        url = reverse('admin:auth_user_change', args=[profile.user.id])
        return format_html(f'<a href="{url}">{profile.user.get_full_name()}</a>')

    user_link.short_description = 'User'

    def username(self, profile: models.UserProfile) -> str:
        return profile.user.username

    username.short_description = 'Username'

    def mfa_status(self, profile: models.UserProfile) -> str:
        return 'Required' if profile.requires_mfa() else 'Not Required'

    mfa_status.short_description = 'MFA Status'

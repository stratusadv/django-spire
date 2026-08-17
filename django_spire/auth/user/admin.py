from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.tools import add_user_to_all_user_group

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    actions = ('add_to_all_user_group',)

    list_display = ('id', 'username', 'email', 'full_name', 'is_active', 'view_user_profile_link')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('username',)
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')

    @admin.action(description='Add to All Users Group')
    def add_to_all_user_group(self, request: HttpRequest, queryset: QuerySet[AuthUser]) -> None:
        updated = 0

        for user in queryset:
            add_user_to_all_user_group(user)
            updated += 1

        self.message_user(request, f'Updated {updated} users.')

    @admin.display(description='Full Name')
    def full_name(self, user: AuthUser) -> str:
        return user.get_full_name()

    @admin.display(description='Profile Link')
    def view_user_profile_link(self, user: AuthUser) -> str:
        url = reverse('django_spire:auth:user:page:detail', kwargs={'pk': user.pk})

        return format_html('<a href="{}">Profile</a>', url)

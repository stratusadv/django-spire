from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.permission import models


@admin.register(models.PortalGroup)
class PortalGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'view_group_detail_link', 'user_count')
    search_fields = ('id', 'name')
    ordering = ('name',)

    def view_group_detail_link(self, group: models.PortalGroup) -> str:
        url = reverse('permission:group_detail', kwargs={'pk': group.pk})
        return format_html(f'<a href="{url}">View Details</a>')

    view_group_detail_link.short_description = 'Details Link'

    def user_count(self, group: models.PortalGroup) -> int:
        return group.user_set.count()

    user_count.short_description = 'User Count'


@admin.register(models.PortalUser)
class PortalUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'full_name', 'is_active', 'view_user_profile_link')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    def full_name(self, user: models.PortalUser) -> str:
        return user.get_full_name()

    full_name.short_description = 'Full Name'

    def view_user_profile_link(self, user: models.PortalUser) -> str:
        url = reverse('user_account:profile:page:detail', kwargs={'pk': user.pk})
        return format_html(f'<a href="{url}">Profile</a>')

    view_user_profile_link.short_description = 'Profile Link'

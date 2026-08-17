from django.contrib import admin
from django.contrib.auth.models import Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'name', 'content_type', 'content_type__app_label')
    list_select_related = ('content_type',)
    ordering = ('content_type__app_label', 'codename')
    search_fields = ('codename', 'name', 'content_type__app_label')

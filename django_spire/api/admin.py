from django.contrib import admin

from django_spire.api.models import ApiAccess


@admin.register(ApiAccess)
class ApiAccessAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission', 'key_hint', 'created_datetime')
    readonly_fields = ('hashed_key', 'permission', 'key_hint', 'created_datetime')

from django.contrib import admin

from django_spire.api.models import ApiAccess


@admin.register(ApiAccess)
class ApiAccessAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_hint',)
    readonly_fields = ('hashed_key', 'key_hint',)

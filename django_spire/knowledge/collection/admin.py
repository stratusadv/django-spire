from django.contrib import admin
from .models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_deleted']
    list_select_related = ['parent']
    list_filter = ['is_deleted', 'is_active']
    search_fields = ['name', 'description', 'parent__name']
    ordering = ['name']
    autocomplete_fields = ['parent']

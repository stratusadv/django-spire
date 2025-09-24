from django.contrib import admin
from .models import Collection, CollectionGroup


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'is_deleted']
    list_select_related = ['parent']
    list_filter = ['is_deleted', 'is_active']
    search_fields = ['id', 'name', 'description', 'parent__name']
    ordering = ['name']
    autocomplete_fields = ['parent']


@admin.register(CollectionGroup)
class CollectionGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'collection', 'auth_group']
    list_select_related = ['collection', 'auth_group']
    search_fields = ['id', 'collection__name', 'auth_group__name']

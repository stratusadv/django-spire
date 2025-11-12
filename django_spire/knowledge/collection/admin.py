from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet
from django.contrib import messages

from .models import Collection, CollectionGroup


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'is_deleted', 'tag_count']
    list_select_related = ['parent']
    list_filter = ['is_deleted', 'is_active']
    search_fields = ['id', 'name', 'description', 'parent__name']
    ordering = ['name']
    autocomplete_fields = ['parent']
    actions = ['set_tags_for_collections']

    @admin.action(description="Set Tags for Collections (Allow 5 Seconds Per)")
    def set_tags_for_collections(self, request, queryset: QuerySet[Collection]):
        processed = 0
        for collection in queryset:
            collection.services.tag.process_and_set_tags()
            processed += 1

        messages.success(request, f'Successfully processed {processed} collections.')

    def tag_count(self, collection: Collection):
        return collection.tags.count()

    tag_count.short_description = 'Tags'


@admin.register(CollectionGroup)
class CollectionGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'collection', 'auth_group']
    list_select_related = ['collection', 'auth_group']
    search_fields = ['id', 'collection__name', 'auth_group__name']



from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin, messages
from django.db.models import Count

from .models import Collection, CollectionGroup

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


TAG_ACTION_MAX_ROWS = 25


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    actions = ('set_tags_for_collections',)
    autocomplete_fields = ('parent',)

    list_display = ('id', 'name', 'parent', 'is_deleted', 'tag_count')
    list_filter = ('is_deleted', 'is_active')
    list_select_related = ('parent',)
    ordering = ('name',)
    search_fields = ('id', 'name', 'description', 'parent__name')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Collection]:
        queryset = super().get_queryset(request)

        return queryset.annotate(_tag_count=Count('tags', distinct=True))

    @admin.action(description='Set Tags for Collections (Allow 5 Seconds Per)')
    def set_tags_for_collections(
        self,
        request: HttpRequest,
        queryset: QuerySet[Collection],
    ) -> None:
        if queryset.count() > TAG_ACTION_MAX_ROWS:
            message = (
                f'Select at most {TAG_ACTION_MAX_ROWS} collections at a time. '
                f'Tagging runs inline and will time out on larger selections.'
            )

            messages.error(request, message)
            return

        processed = 0

        for collection in queryset:
            collection.services.tag.process_and_set_tags()
            processed += 1

        messages.success(request, f'Successfully processed {processed} collections.')

    @admin.display(description='Tags', ordering='_tag_count')
    def tag_count(self, collection: Collection) -> int:
        return collection._tag_count


@admin.register(CollectionGroup)
class CollectionGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'collection', 'auth_group')
    list_select_related = ('collection', 'auth_group')
    search_fields = ('id', 'collection__name', 'auth_group__name')

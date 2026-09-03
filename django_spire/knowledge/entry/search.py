from __future__ import annotations

from typing import TYPE_CHECKING

from django.http.request import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search
from django_spire.knowledge.entry.models import Entry

if TYPE_CHECKING:
    from django.db.models import QuerySet


class EntrySearch(Search):
    model_class = Entry
    searchable_fields = ['name', '_search_text']
    search_key = 'ENTRY'
    name = 'Knowledge Entries'
    icon = 'bi-book'
    permission_required = 'django_spire_knowledge.view_collection'

    def base_queryset(self, request: HttpRequest) -> QuerySet[Entry]:
        return self.model_class.objects.active().select_related('collection')

    def generate_list_url(self) -> str:
        return reverse('django_spire:knowledge:page:home')

    def generate_detail_url(self, obj: Entry) -> str:
        return reverse('django_spire:knowledge:entry:version:page:editor', kwargs={'pk': obj.pk})

    def result_name(self, obj: Entry) -> str:
        return obj.name

    def result_description(self, obj: Entry) -> str:
        return obj.collection.name

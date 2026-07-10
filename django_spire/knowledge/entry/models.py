from __future__ import annotations

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.contrib.utils import truncate_string
from django_spire.core.tag.mixins import TagModelMixin
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.querysets import EntryQuerySet
from django_spire.knowledge.entry.services.service import EntryService
from django_spire.knowledge.entry.version.models import EntryVersion


class Entry(HistoryModelMixin, OrderingModelMixin, TagModelMixin, ActivityMixin):
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name='entries', related_query_name='entry'
    )
    current_version = models.OneToOneField(
        EntryVersion,
        on_delete=models.CASCADE,
        related_name='current_version',
        related_query_name='current_version',
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=255)

    _search_text = models.TextField(blank=True, default='')
    _search_vector = SearchVectorField(null=True)

    objects = EntryQuerySet.as_manager()
    services = EntryService()

    def __str__(self):
        return self.name

    @property
    def name_short(self) -> str:
        return truncate_string(self.name, 32)

    @property
    def top_level_collection(self) -> Collection:
        return self.collection.top_level_parent

    class Meta:
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'
        db_table = 'django_spire_knowledge_entry'
        indexes = [
            GinIndex(fields=['_search_vector'], name='entry_search_vector_idx'),
            GinIndex(name='entry_name_trgm_idx', fields=['name'], opclasses=['gin_trgm_ops']),
            GinIndex(
                name='entry_search_text_trgm_idx',
                fields=['_search_text'],
                opclasses=['gin_trgm_ops'],
            ),
        ]

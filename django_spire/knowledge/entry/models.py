from django.db import models

from django_spire.contrib.ordering.model_mixin import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.querysets import EntryQuerySet
from django_spire.knowledge.entry.services.service import EntryService
from django_spire.knowledge.entry.version.models import EntryVersion


class Entry(HistoryModelMixin, OrderingModelMixin):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='entries',
        related_query_name='entry'
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

    objects = EntryQuerySet.as_manager()
    services = EntryService()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'
        db_table = 'django_spire_knowledge_entry'

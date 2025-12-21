from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.contrib import Breadcrumbs
from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.core.tag.mixins import TagModelMixin
from django_spire.contrib.utils import truncate_string
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.querysets import EntryQuerySet
from django_spire.knowledge.entry.services.service import EntryService
from django_spire.knowledge.entry.version.models import EntryVersion


class Entry(
    HistoryModelMixin,
    OrderingModelMixin,
    TagModelMixin
):
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

    @property
    def name_short(self) -> str:
        return truncate_string(self.name, 32)

    @property
    def top_level_collection(self) -> Collection:
        return self.collection.top_level_parent

    def base_breadcrumb(self) -> Breadcrumbs:
        bread_crumbs = Breadcrumbs()

        bread_crumbs.add_breadcrumb(
            self.top_level_collection.name_short,
            reverse(
                'django_spire:knowledge:collection:page:top_level',
                kwargs={'pk': self.top_level_collection.pk}
            )
        )

        bread_crumbs.add_breadcrumb(
            self.collection.name_short
        )

        bread_crumbs.add_breadcrumb(
            self.name_short,
        )

        return bread_crumbs

    class Meta:
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'
        db_table = 'django_spire_knowledge_entry'

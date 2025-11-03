from __future__ import annotations

from django.db import models

from django_spire.auth.group.models import AuthGroup
from django_spire.contrib import Breadcrumbs
from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.contrib.utils import truncate_string
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.collection.querysets import CollectionQuerySet
from django_spire.knowledge.collection.services.service import CollectionGroupService, \
    CollectionService


class Collection(HistoryModelMixin, OrderingModelMixin):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        related_query_name='child',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)
    description = models.TextField()

    services = CollectionService()
    objects = CollectionQuerySet.as_manager()

    def __str__(self):
        return self.name

    @property
    def name_short(self) -> str:
        return truncate_string(self.name, 32)

    @property
    def top_level_parent(self) -> Collection:
        if self.parent is None:
            return self

        return self.parent.top_level_parent

    def base_breadcrumb(self) -> Breadcrumbs:
        breadcrumbs = Breadcrumbs()

        breadcrumbs.add_breadcrumb(self.name_short)

        return breadcrumbs

    class Meta:
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        db_table = 'django_spire_knowledge_collection'
        permissions = [
            ('can_access_all_collections', 'Can Access All Collections'),
            ('can_change_collection_groups', 'Can Change Collection Groups'),
        ]


class CollectionGroup(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='groups',
        related_query_name='group',
    )

    auth_group = models.ForeignKey(
        AuthGroup,
        on_delete=models.CASCADE,
        related_name='collection_groups',
        related_query_name='collection_group',
    )

    services = CollectionGroupService()

    def __str__(self):
        return f'{self.collection.name} - {self.auth_group.name}'
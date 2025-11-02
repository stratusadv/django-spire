from __future__ import annotations

from django.db import models

from django_spire.auth.group.models import AuthGroup
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
        return truncate_string(self.name, 20)

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

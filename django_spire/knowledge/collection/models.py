from django.db import models

from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.collection.querysets import CollectionQuerySet
from django_spire.knowledge.collection.services.service import CollectionService


class Collection(HistoryModelMixin):
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
    objects = CollectionQuerySet().as_manager()

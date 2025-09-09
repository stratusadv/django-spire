from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse

from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.collection.querysets import CollectionQuerySet
from django_spire.knowledge.collection.services.service import CollectionService


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

    @property
    def delete_url(self) -> str:
        site = Site.objects.get_current() if not settings.DEBUG else ''
        path = reverse(
            'django_spire:knowledge:collection:page:delete',
            kwargs={'pk': self.pk},
        )[1:]
        return f'{site}/{path}'

    @property
    def create_entry_url(self) -> str:
        site = Site.objects.get_current() if not settings.DEBUG else ''
        path = reverse(
            'django_spire:knowledge:entry:form:create',
            kwargs={'collection_pk': self.pk},
        )[1:]
        return f'{site}/{path}'

    @property
    def import_entry_url(self) -> str:
        site = Site.objects.get_current() if not settings.DEBUG else ''
        path = reverse(
            'django_spire:knowledge:entry:form:import',
            kwargs={'collection_pk': self.pk},
        )[1:]
        return f'{site}/{path}'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        db_table = 'django_spire_knowledge_collection'

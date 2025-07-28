from django.db import models
from django.utils.timezone import now

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.ordering.model_mixin import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.choices import EntryVersionTypeChoices
from django_spire.knowledge.entry.querysets import EntryQuerySet, EntryVersionQuerySet
from django_spire.knowledge.entry.services.service import EntryVersionService, EntryService


class Entry(HistoryModelMixin, OrderingModelMixin):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='entries',
        related_query_name='entry'
    )
    current_version = models.OneToOneField(
        'EntryVersion',
        on_delete=models.CASCADE,
        related_name='current_version',
        related_query_name='current_version',
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=255)

    objects = EntryQuerySet.as_manager()
    services = EntryService()


class EntryVersion(HistoryModelMixin):
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name='versions',
        related_query_name='version'
    )
    author = models.ForeignKey(
        AuthUser,
        on_delete=models.CASCADE,
        related_name='entry_versions',
        related_query_name='entry_version'
    )
    published_datetime = models.DateTimeField(blank=True, null=True)
    last_edit_datetime = models.DateTimeField(default=now)

    status = models.CharField(
        max_length=32,
        choices=EntryVersionTypeChoices,
        default=EntryVersionTypeChoices.DRAFT
    )

    objects = EntryVersionQuerySet.as_manager()
    services = EntryVersionService()

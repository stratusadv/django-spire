from django.db import models

from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.choices import EntryRevisionTypeChoices


class Entry(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='entries',
        related_query_name='entry'
    )
    current_revision = models.OneToOneField(
        'EntryRevision',
        on_delete=models.CASCADE,
        related_name='current_entry',
        related_query_name='current_entry'
    )


class EntryRevision(models.Model):
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name='revisions',
        related_query_name='revision'
    )

    type = models.CharField(max_length=32, choices=EntryRevisionTypeChoices, default=EntryRevisionTypeChoices.DRAFT)


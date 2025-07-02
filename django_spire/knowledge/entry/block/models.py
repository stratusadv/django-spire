from django.db import models

from django_spire.knowledge.entry.models import EntryRevision
from django_spire.knowledge.entry.block.choices import EntryBlockTypeChoices


class EntryBlock(models.Model):
    revision = models.ForeignKey(
        EntryRevision,
        on_delete=models.CASCADE,
        related_name='snippets',
        related_query_name='snippet'
    )
    type = models.CharField(
        max_length=32,
        choices=EntryBlockTypeChoices,
        default=EntryBlockTypeChoices.TEXT
    )
    block_data = models.JSONField()
    text_data = models.TextField()
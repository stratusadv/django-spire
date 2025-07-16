from django.db import models

from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.block.maps import ENTRY_BLOCK_MAP
from django_spire.knowledge.entry.editor.blocks.block import BaseBlock
from django_spire.knowledge.entry.models import EntryVersion
from django_spire.knowledge.entry.querysets import EntryVersionBlockQuerySet


class EntryVersionBlock(HistoryModelMixin):
    version = models.ForeignKey(
        EntryVersion,
        on_delete=models.CASCADE,
        related_name='blocks',
        related_query_name='block'
    )
    type = models.CharField(
        max_length=32,
        choices=BlockTypeChoices,
        default=BlockTypeChoices.TEXT
    )
    _block_data = models.JSONField()
    _text_data = models.TextField()

    @property
    def block(self) -> BaseBlock:
        return ENTRY_BLOCK_MAP[self.type](**self._block_data)

    @block.setter
    def block(self, value: BaseBlock):
        self.type = value.type
        self._block_data = value.model_dump()
        self._text_data = value.render_to_text()

    objects = EntryVersionBlockQuerySet.as_manager()

from __future__ import annotations

from django.db import models

from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.maps import ENTRY_BLOCK_MAP, \
    EDITOR_BLOCK_DATA_MAP
from django_spire.knowledge.entry.version.block.services.service import EntryVersionBlockService
from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock
from django_spire.knowledge.entry.version.block.entities import BaseEditorBlockData
from django_spire.knowledge.entry.version.models import EntryVersion
from django_spire.knowledge.entry.version.block.querysets import EntryVersionBlockQuerySet


class EntryVersionBlock(HistoryModelMixin, OrderingModelMixin):
    version = models.ForeignKey(
        EntryVersion,
        on_delete=models.CASCADE,
        related_name='blocks',
        related_query_name='block'
    )

    editor_id = models.CharField(max_length=32, null=True, blank=True)

    type = models.CharField(
        max_length=32,
        choices=BlockTypeChoices,
        default=BlockTypeChoices.TEXT
    )

    _block_data = models.JSONField()
    _text_data = models.TextField()


    _editor_block_data = models.JSONField(null=True, blank=True)
    _tunes_data = models.JSONField(null=True, blank=True)
    _new_text_data = models.TextField(null=True, blank=True)

    objects = EntryVersionBlockQuerySet.as_manager()
    services = EntryVersionBlockService()

    @property
    def block(self) -> BaseBlock:
        return ENTRY_BLOCK_MAP[self.type](**self._editor_block_data)


    @block.setter
    def block(self, value: BaseBlock):
        # self.type = value.type
        self._block_data = value.model_dump()
        self._text_data = value.render_to_text()

    @property
    def editor_block_data(self) -> BaseEditorBlockData:
        return EDITOR_BLOCK_DATA_MAP[self.type](**self._editor_block_data)

    @editor_block_data.setter
    def editor_block_data(self, block: BaseEditorBlockData):
        self._block_data = block.model_dump()
        self._text_data = block.render_to_text()

    def render_to_text(self) -> str:
        return self.editor_block_data.render_to_text()

    class Meta:
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'
        db_table = 'django_spire_knowledge_entry_version_block'

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.maps import EDITOR_JS_BLOCK_DATA_MAP
from django_spire.knowledge.entry.version.block.querysets import EntryVersionBlockQuerySet
from django_spire.knowledge.entry.version.block.services.service import EntryVersionBlockService
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.data.data import BaseEditorJsBlockData


class EntryVersionBlock(HistoryModelMixin, OrderingModelMixin):
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

    # contains data related to EditorJS tunes,
    # which are additional modifications to blocks (e.g. footnotes, etc.)
    # https://editorjs.io/block-tunes-api/
    _tunes_data = models.JSONField(null=True, blank=True)

    objects = EntryVersionBlockQuerySet.as_manager()
    services = EntryVersionBlockService()

    @property
    def editor_js_block_data(self) -> BaseEditorJsBlockData:
        return EDITOR_JS_BLOCK_DATA_MAP[self.type](**self._block_data)

    @editor_js_block_data.setter
    def editor_js_block_data(self, value: BaseEditorJsBlockData):
        # exclude_none=True ensures that block meta objects aren't autofilled with keys,
        # which can mess up editor rendering
        self._block_data = value.model_dump(exclude_none=True)
        self._text_data = value.render_to_text()

    def update_editor_js_block_data_from_dict(self, value: dict):
        self.editor_js_block_data = EDITOR_JS_BLOCK_DATA_MAP[self.type](**value)

    def render_to_text(self) -> str:
        return self.editor_js_block_data.render_to_text()

    class Meta:
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'
        db_table = 'django_spire_knowledge_entry_version_block'

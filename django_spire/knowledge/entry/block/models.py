from django.db import models
from django.forms import model_to_dict
from django.template.loader import render_to_string

from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.block.maps import ENTRY_BLOCK_MAP
from django_spire.knowledge.entry.block.services.service import EntryVersionBlockService
from django_spire.knowledge.entry.editor.blocks.block import BaseBlock
from django_spire.knowledge.entry.models import EntryVersion
from django_spire.knowledge.entry.block.querysets import EntryVersionBlockQuerySet


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
    order = models.PositiveIntegerField()
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

    def to_dict(self) -> dict:
        return {
            **model_to_dict(
                self,
                fields=['id', 'order', 'type'],
            ),
            'block': {
                'value': self.block.value,
                'type': self.block.type,
                'update_template_rendered': render_to_string(
                    context={
                        'version_block': self,
                        'value': self.block.value,
                    },
                    template_name=self.block.update_template,
                )
            }
        }

    objects = EntryVersionBlockQuerySet.as_manager()
    services = EntryVersionBlockService()

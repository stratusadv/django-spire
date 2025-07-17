from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.block.choices import BlockTypeChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.block.models import EntryVersionBlock


class EntryVersionBlockFactoryService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    @staticmethod
    def create_blank_text_block() -> EntryVersionBlock:
        return EntryVersionBlock.objects.create(
            type=BlockTypeChoices.TEXT,
            order=0,
            _block_data={},
            _text_data='',
        )

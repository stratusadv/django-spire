from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.block.maps import ENTRY_BLOCK_MAP

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import EntryVersion
    from django_spire.knowledge.entry.block.models import EntryVersionBlock


class EntryVersionBlockFactoryService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def create_blank_block(
            self,
            entry_version: EntryVersion,
            block_type: BlockTypeChoices,
            order: int,
    ) -> EntryVersionBlock:
        self.obj = self.obj_class(
            version=entry_version,
            type=block_type,
            order=order,
        )
        self.obj.block = ENTRY_BLOCK_MAP[block_type](value='', type=block_type)
        self.obj.save()
        return self.obj

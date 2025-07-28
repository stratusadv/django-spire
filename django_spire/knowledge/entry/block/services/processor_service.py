from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING, Any

from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.block.maps import ENTRY_BLOCK_MAP

if TYPE_CHECKING:
    from django_spire.knowledge.entry.block.models import EntryVersionBlock


class EntryVersionBlockProcessorService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def update(self, value: Any, block_type: BlockTypeChoices):
        self.obj.block = ENTRY_BLOCK_MAP[block_type](value=value, type=block_type)
        self.obj.save()
        return self.obj

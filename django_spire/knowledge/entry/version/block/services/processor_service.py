from __future__ import annotations

from copy import deepcopy

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING, Any

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockProcessorService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def update_block(self, value: Any, block_type: BlockTypeChoices):
        block = deepcopy(self.obj.block)
        block.value = value
        block.type = block_type
        self.obj.block = block
        self.obj.save()
        return self.obj

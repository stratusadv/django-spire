from __future__ import annotations

from copy import deepcopy

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING, Any

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockProcessorService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def set_deleted(self):
        self.obj.ordering_services.processor.remove_from_objects(
            destination_objects=self.obj.version.blocks.active()
        )

        self.obj.set_deleted()

    def update_block(self, value: Any, block_type: BlockTypeChoices):
        block = deepcopy(self.obj.block)
        block.value = value
        block.type = block_type

        self.obj.block = block
        self.obj.save()

        return self.obj

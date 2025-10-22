from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.maps import EDITOR_BLOCK_DATA_MAP
from django_spire.knowledge.entry.version.block.services.factory_service import \
    EntryVersionBlockFactoryService
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock
    factory = EntryVersionBlockFactoryService()

    def save_model_obj(
            self,
            entry_version: EntryVersion,
            block_type: BlockTypeChoices,
            block_order: int,
            block_data: dict,
            block_tunes: dict,
            commit: bool = True,
            **kwargs: dict
    ) -> EntryVersionBlock:
        self.obj.version = entry_version
        self.obj.type = block_type
        self.obj.order = block_order
        self.obj.tunes = block_tunes
        self.obj.editor_block_data = EDITOR_BLOCK_DATA_MAP[block_type](**block_data)

        self.obj.clean()

        if commit:
            self.obj.save()

        return self.obj
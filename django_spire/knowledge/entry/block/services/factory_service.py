from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.block.choices import BlockTypeChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import EntryVersion
    from django_spire.knowledge.entry.block.models import EntryVersionBlock


class EntryVersionBlockFactoryService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def create_blank_text_block(self, version: EntryVersion) -> EntryVersionBlock:
        return self.obj_class.create(
            version=version,
            type=BlockTypeChoices.TEXT,
            order=0,
            _block_data={'value': '', 'type': BlockTypeChoices.TEXT.value},
            _text_data='',
        )

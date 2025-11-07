from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.block.data.maps import EDITOR_BLOCK_DATA_MAP
from django_spire.knowledge.entry.version.maps import FILE_TYPE_CONVERTER_MAP

if TYPE_CHECKING:
    from django_spire.file.models import File
    from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
    from django_spire.knowledge.entry.version.models import EntryVersion


class EntryVersionBlockFactoryService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def create_blocks_from_file(
            self,
            file: File,
            entry_version: EntryVersion
    ) -> list[EntryVersionBlock]:
        if file.type not in FILE_TYPE_CONVERTER_MAP:
            return []

        converter = FILE_TYPE_CONVERTER_MAP[file.type](entry_version=entry_version)

        return self.obj_class.objects.bulk_create(
            converter.convert_file_to_blocks(file=file)
        )

    def create_validated_block(
            self,
            entry_version: EntryVersion,
            block_type: BlockTypeChoices,
            block_data: dict,
            block_order: int,
            block_tunes: dict = {},
            **kwargs,
    ):
        self.obj.version = entry_version
        self.obj.type = block_type
        self.obj.order = block_order
        self.obj.tunes = block_tunes
        self.obj.editor_block_data = EDITOR_BLOCK_DATA_MAP[block_type](**block_data)

        self.obj.clean()

        return self.obj

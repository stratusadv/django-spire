from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.block.maps import ENTRY_BLOCK_MAP
from django_spire.knowledge.entry.version.maps import FILE_TYPE_CONVERTER_MAP

if TYPE_CHECKING:
    from django_spire.file.models import File
    from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
    from django_spire.knowledge.entry.version.models import EntryVersion


class EntryVersionBlockFactoryService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def create_blank_block(
            self,
            entry_version: EntryVersion,
            block_type: BlockTypeChoices,
            order: int,
            **kwargs
    ) -> EntryVersionBlock:
        self.obj = self.obj_class(
            version=entry_version,
            type=block_type,
            order=order,
        )
        self.obj.block = ENTRY_BLOCK_MAP[block_type](
            value='',
            type=block_type,
            **kwargs
        )
        self.obj.save()
        return self.obj

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

    def create_null_block(
            self,
            entry_version: EntryVersion,
            block_type: BlockTypeChoices,
            order: int,
            value: str
    ):
        self.obj = self.obj_class(
            version=entry_version,
            type=block_type,
            order=order
        )
        block = ENTRY_BLOCK_MAP[block_type](type=block_type, value=value,)
        self.obj.block = block
        return self.obj

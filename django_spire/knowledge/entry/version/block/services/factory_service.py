from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.block.entities import EditorBlock
from django_spire.knowledge.entry.version.block.maps import ENTRY_BLOCK_MAP, \
    EDITOR_BLOCK_DATA_MAP
from django_spire.knowledge.entry.version.maps import FILE_TYPE_CONVERTER_MAP

if TYPE_CHECKING:
    from django_spire.file.models import File
    from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
    from django_spire.knowledge.entry.version.models import EntryVersion


class EntryVersionBlockFactoryService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def from_editor_block(self, editor_block: EditorBlock, entry_version: EntryVersion):
        return self.obj_class(
            version=entry_version,
            type=editor_block.type,
            order=editor_block.order,
            block=EDITOR_BLOCK_DATA_MAP[editor_block.type](**editor_block.data),
        )


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
            value: str,
            **kwargs,
    ):
        self.obj = self.obj_class(
            version=entry_version,
            type=block_type,
            order=order
        )
        block = ENTRY_BLOCK_MAP[block_type](
            type=block_type,
            value=value,
            **kwargs
        )
        self.obj.block = block
        return self.obj

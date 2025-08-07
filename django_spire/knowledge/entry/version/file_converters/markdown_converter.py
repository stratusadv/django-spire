from __future__ import annotations

import marko

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.file_converters.converter import \
    BaseFileConverter
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.models import EntryVersion


class MarkdownConverter(BaseFileConverter):
    def convert_to_model_objects(
            self,
            entry_version: EntryVersion
    ) -> list[EntryVersionBlock]:
        blocks = []
        with open(self.file.file.path, 'r') as f:
            syntax_tree = marko.parse(f.read())

            for child in syntax_tree.children:
                blocks.append(
                    EntryVersionBlock(
                        version=entry_version,
                        type=self._get_type_from_marko_child(child),
                    )
                )

        return blocks

    @staticmethod
    def _get_type_from_marko_child(child: marko.block) -> BlockTypeChoices:
        return BlockTypeChoices.TEXT

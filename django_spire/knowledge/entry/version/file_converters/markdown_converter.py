from __future__ import annotations

import marko

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.file_converters.converter import \
    BaseFileConverter
from django_spire.knowledge.entry.version.block import models

if TYPE_CHECKING:
    from marko.element import Element


# For more info on Marko:
# https://marko-py.readthedocs.io/en/latest/api.html#marko.block.BlockElement
class MarkdownConverter(BaseFileConverter):
    def convert_to_model_objects(self) -> list[models.EntryVersionBlock]:
        blocks = []
        with open(self.file.file.path, 'r') as f:
            syntax_tree = marko.parse(f.read())

            for marko_block in syntax_tree.children:
                blocks.append(self._marko_block_to_version_block(marko_block))

        return blocks

    def _marko_block_to_version_block(
            self,
            marko_block: Element
    ) -> models.EntryVersionBlock:
        mark_block_name = marko_block.__class__.__name__

        if mark_block_name == 'Heading':
            return self._convert_heading_block(marko_block)

        if mark_block_name == 'Paragraph':
            return self._convert_paragraph_block(marko_block)

        if mark_block_name == 'BlankLine':
            return models.EntryVersionBlock(
                version=self.entry_version,
                type=models.BlockTypeChoices.TEXT,
                _text_data='',

            )

        return models.EntryVersionBlock(
            version=self.entry_version,
        )

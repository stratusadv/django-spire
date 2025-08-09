from __future__ import annotations

import html
import re

import marko

from typing import Sequence, TYPE_CHECKING

from marko.element import Element

from django_spire.knowledge.entry.version.block.blocks.heading_block import HeadingBlock
from django_spire.knowledge.entry.version.block.blocks.text_block import TextBlock
from django_spire.knowledge.entry.version.file_converters.converter import \
    BaseFileConverter
from django_spire.knowledge.entry.version.block import models

if TYPE_CHECKING:
    from marko.block import BlockElement, Heading


# For more info on Marko:
# https://marko-py.readthedocs.io/en/latest/api.html#marko.block.BlockElement
class MarkdownConverter(BaseFileConverter):
    # TODO: Use render with string html tags to get value of mark blocks.
    # self.strip_html_tags(text=marko.render(syntax_tree.children[1]))
    @staticmethod
    def strip_html_tags(text):
        clean = re.sub(r'<[^>]+>', '', text)
        return html.unescape(clean)

    def convert_to_model_objects(self) -> list[models.EntryVersionBlock]:
        blocks = []
        with open(self.file.file.path, 'r') as f:
            syntax_tree = marko.parse(f.read())

            for order, marko_block in enumerate(syntax_tree.children):
                blocks.append(
                    self._marko_block_to_version_block(
                        marko_block=marko_block,
                        order=order
                    )
                )

        return blocks

    def _convert_heading_block(
            self,
            marko_block: Heading | BlockElement,
            order: int
    ) -> models.EntryVersionBlock:
        heading_type = (
            models.BlockTypeChoices.HEADING
            if marko_block.level == 1
            else models.BlockTypeChoices.SUB_HEADING
        )

        return models.EntryVersionBlock.services.factory.create_null_block(
            entry_version=self.entry_version,
            block_type=heading_type,
            order=order,
            value=self._get_mark_block_content(marko_block)
        )

    def _get_mark_block_content(
            self,
            marko_block: BlockElement | Sequence[Element]
    ) -> str:
        if not hasattr(marko_block, 'children'):
            return ''

        if isinstance(marko_block.children, str):
            return marko_block.children

        return self._get_mark_block_content(marko_block.children)

    def _marko_block_to_version_block(
            self,
            marko_block: BlockElement | Element,
            order: int
    ) -> models.EntryVersionBlock:
        mark_block_name = marko_block.__class__.__name__

        if mark_block_name == 'Heading':
            return self._convert_heading_block(marko_block=marko_block, order=order)

        return models.EntryVersionBlock.services.factory.create_null_block(
            entry_version=self.entry_version,
            block_type=models.BlockTypeChoices.TEXT,
            order=order,
            value=self._get_mark_block_content(marko_block)
        )

from __future__ import annotations

import html
import re

import marko

from typing import TYPE_CHECKING

from marko.element import Element
from marko.block import Heading

from django_spire.knowledge.entry.version.converters.converter import \
    BaseConverter
from django_spire.knowledge.entry.version.block import models

if TYPE_CHECKING:
    from django_spire.file.models import File
    from marko.block import BlockElement


class MarkdownConverter(BaseConverter):
    """Converts Markdown content to a list of EntryVersionBlocks using Marko.

    For more info on Marko:
    https://marko-py.readthedocs.io/en/latest/api.html#marko.block.BlockElement
    """

    def convert_file_to_blocks(self, file: File) -> list[models.EntryVersionBlock]:
        with open(file.file.path, 'r') as f:
            return self.convert_markdown_to_blocks(f.read())

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
            value=self._get_marko_text_content(marko_block),
        )

    def convert_markdown_to_blocks(
            self,
            markdown_content: str
    ) -> list[models.EntryVersionBlock]:
        syntax_tree = marko.parse(markdown_content)

        blocks = []
        for order, marko_block in enumerate(syntax_tree.children):
            blocks.append(
                self._marko_block_to_version_block(
                    marko_block=marko_block, order=order + 1
                )
            )

        return blocks

    def _get_marko_text_content(
            self,
            marko_block: BlockElement
    ) -> str:
        return self._strip_html_tags(marko.render(marko_block))

    def _marko_block_to_version_block(
            self,
            marko_block: BlockElement | Element,
            order: int
    ) -> models.EntryVersionBlock:
        if isinstance(marko_block, Heading):
            return self._convert_heading_block(marko_block=marko_block, order=order)

        return models.EntryVersionBlock.services.factory.create_null_block(
            entry_version=self.entry_version,
            block_type=models.BlockTypeChoices.TEXT,
            order=order,
            value=self._get_marko_text_content(marko_block)
        )

    @staticmethod
    def _strip_html_tags(text: str) -> str:
        return html.unescape(re.sub(r'<[^>]+>', '', text))

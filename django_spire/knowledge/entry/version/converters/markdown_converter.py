from __future__ import annotations

import html
import re

import marko

from typing import TYPE_CHECKING

from marko.element import Element
from marko.block import Heading, List, ListItem

from django_spire.knowledge.entry.version.converters.converter import \
    BaseConverter
from django_spire.knowledge.entry.version.block import models

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.models import EntryVersion
    from django_spire.file.models import File
    from marko.block import BlockElement


class MarkdownConverter(BaseConverter):
    """Converts Markdown content to a list of EntryVersionBlocks using Marko.

    For more info on Marko:
    https://marko-py.readthedocs.io/en/latest/api.html#marko.block.BlockElement
    """
    def __init__(self, entry_version: EntryVersion):
        super().__init__(entry_version)
        self.last_order = 0

    def convert_file_to_blocks(self, file: File) -> list[models.EntryVersionBlock]:
        with open(file.file.path, 'r') as f:
            return self.convert_markdown_to_blocks(f.read())

    def _convert_heading_block(
            self,
            marko_block: Heading,
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

    def _convert_list_block(
            self,
            marko_block: List | ListItem | Element,
            bullet: str,
            indent_level: int = 0
    ) -> list[models.EntryVersionBlock]:
        if not marko_block.children:
            list_item_block = models.EntryVersionBlock.services.factory.create_null_block(
                entry_version=self.entry_version,
                block_type=models.BlockTypeChoices.LIST_ITEM,
                order=self.last_order,
                value=self._get_marko_text_content(marko_block),
                bullet=bullet,
                indent_level=indent_level,
                ordered=marko_block.ordered,
            )
            self.last_order += 1
            return [list_item_block]

        blocks = []
        for child in marko_block.children:
            if bullet.endswith('.'):
                bullet = bullet.rstrip('.')
                bullet = str(int(bullet) + 1) + '.'

            blocks.extend(
                self._convert_list_block(
                    marko_block=child,
                    bullet=bullet,
                    indent_level=indent_level + 1,
                )
            )

        return blocks

    def convert_markdown_to_blocks(
            self,
            markdown_content: str
    ) -> list[models.EntryVersionBlock]:
        syntax_tree = marko.parse(markdown_content)

        blocks = []
        for marko_block in syntax_tree.children:
            if isinstance(marko_block, List):
                blocks.extend(
                    self._convert_list_block(
                        marko_block=marko_block,
                        bullet=marko_block.bullet,

                    )
                )
            else:
                blocks.append(
                    self._marko_block_to_version_block(
                        marko_block=marko_block,
                        order=self.last_order,
                    )
                )
                self.last_order += 1

        return blocks

    @staticmethod
    def _get_marko_text_content(marko_block: BlockElement) -> str:
        html_text = marko.render(marko_block)
        bolded_text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', html_text)
        italicized_text = re.sub(r'<em>(.*?)</em>', r'*\1*', bolded_text)
        strikethrough_text = re.sub(r'<del>(.*?)</del>', r'~~*\1*~~', italicized_text)
        text = re.sub(r'<[^>]+>', '', strikethrough_text)
        return html.unescape(text)

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

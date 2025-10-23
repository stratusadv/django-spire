from __future__ import annotations

import html
import re

import marko

from typing import TYPE_CHECKING

from django.core.files.storage import default_storage
from marko.element import Element
from marko.block import Heading, List, ListItem

from django_spire.knowledge.entry.version.block.data.heading_data import \
    HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import \
    TextEditorBlockData
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
        self._order = 0

    def convert_file_to_blocks(self, file: File) -> list[models.EntryVersionBlock]:
        with default_storage.open(file.file.name, 'r') as f:
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

        return models.EntryVersionBlock.services.factory.create_validated_block(
            entry_version=self.entry_version,
            block_type=heading_type,
            order=order,
            value=self._get_marko_text_content(marko_block),
        )

    def _convert_list_block(
            self,
            marko_block: List | ListItem | Element,
            bullet: str,
            indent_level: int,
            ordered: bool,
    ) -> list[models.EntryVersionBlock]:
        if isinstance(marko_block.children, str):
            list_item_block = models.EntryVersionBlock.services.factory.create_validated_block(
                entry_version=self.entry_version,
                block_type=models.BlockTypeChoices.LIST_ITEM,
                order=self._order,
                value=self._get_marko_text_content(marko_block),
                bullet=bullet,
                indent_level=indent_level,
                ordered=ordered,
            )
            self._order += 1
            return [list_item_block]

        if isinstance(marko_block, ListItem):
            indent_level += 1

        blocks = []
        for child in marko_block.children:
            blocks.extend(
                self._convert_list_block(
                    marko_block=child,
                    bullet=bullet,
                    indent_level=indent_level,
                    ordered=ordered,
                )
            )

            if isinstance(child, ListItem) and bullet.endswith('.'):
                bullet = bullet.rstrip('.')
                bullet = str(int(bullet) + 1) + '.'

        return blocks

    def convert_markdown_to_blocks(
            self,
            markdown_content: str
    ) -> list[models.EntryVersionBlock]:
        parsed_markdown_document = marko.parse(markdown_content)

        return [
            self._marko_block_to_version_block(
                marko_block=marko_block,
                order=i,
            )
            for i, marko_block in enumerate(parsed_markdown_document.children)
        ]

    @staticmethod
    def _get_marko_text_content(marko_block: BlockElement) -> str:
        html_text = marko.render(marko_block)
        bolded_text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', html_text)
        italicized_text = re.sub(r'<em>(.*?)</em>', r'*\1*', bolded_text)
        strikethrough_text = re.sub(r'<del>(.*?)</del>', r'~~*\1*~~', italicized_text)
        text = re.sub(r'<[^>]+>', '', strikethrough_text)
        return html.unescape(text)

    @staticmethod
    def convert_html_text_to_markdown(html_text: str) -> str:
        return marko.convert(html_text)

    def _marko_block_to_version_block(
            self,
            marko_block: BlockElement | Element,
            order: int
    ) -> models.EntryVersionBlock:
        if isinstance(marko_block, Heading):
            editor_block_data = HeadingEditorBlockData(
                text=self._get_marko_text_content(marko_block),
                level=marko_block.level,
            )

        elif isinstance(marko_block, List):
            return self._convert_heading_block(marko_block=marko_block, order=order)

        else:
            editor_block_data = TextEditorBlockData(
                text=self._get_marko_text_content(marko_block)
            )


        return models.EntryVersionBlock.services.factory.create_validated_block(
            entry_version=self.entry_version,
            block_type=models.BlockTypeChoices.TEXT,
            order=order,
            value=self._get_marko_text_content(marko_block)
        )

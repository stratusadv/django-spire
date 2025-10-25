from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import TYPE_CHECKING

import marko
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage
from markitdown.converters import HtmlConverter
from marko.block import Heading, List, ListItem, Paragraph, BlankLine
from marko.element import Element

from django_spire.knowledge.entry.version.block import models
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.list.choices import \
    ListEditorBlockDataStyle
from django_spire.knowledge.entry.version.converters.converter import \
    BaseConverter

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.models import EntryVersion
    from django_spire.file.models import File
    from marko.block import BlockElement


MARKO_BLOCK_TYPE_TO_BLOCK_CHOICES = defaultdict(
    lambda:BlockTypeChoices.TEXT,
    {
        Paragraph: models.BlockTypeChoices.TEXT,
        BlankLine: models.BlockTypeChoices.TEXT,
        Heading: models.BlockTypeChoices.HEADING,
        List: models.BlockTypeChoices.LIST,
    }
)


class MarkdownConverter(BaseConverter):
    """Converts Markdown content to a list of EntryVersionBlocks using Marko.

    For more info on Marko:
    https://marko-py.readthedocs.io/en/latest/api.html#marko.block.BlockElement
    """

    html_converter = HtmlConverter()

    def __init__(self, entry_version: EntryVersion):
        super().__init__(entry_version)
        self._order = 0

    def convert_file_to_blocks(self, file: File) -> list[models.EntryVersionBlock]:
        with default_storage.open(file.file.name, 'r') as f:
            return self.convert_markdown_to_blocks(f.read())

    def convert_markdown_to_blocks(
            self,
            markdown_content: str
    ) -> list[models.EntryVersionBlock]:
        marko_blocks = marko.parse(markdown_content).children

        return [
            models.EntryVersionBlock.services.factory.create_validated_block(
                entry_version=self.entry_version,
                block_type=MARKO_BLOCK_TYPE_TO_BLOCK_CHOICES[marko_block.__class__],
                block_data=self._marko_block_to_editor_block_data_dict(marko_block),
                block_order=order,
                block_tunes={}
            )
            for order, marko_block in enumerate(marko_blocks)
        ]

    @classmethod
    def html_to_markdown(cls, html_content: str) -> str:
        return cls.html_converter.convert_string(html_content).markdown

    @classmethod
    def _remove_outer_html_tags(
            cls,
            html_content: str,
            tag_name: str | None = None,
    ) -> str:
        bs = BeautifulSoup(html_content, 'html.parser')

        if tag_name:
            # Only target specific tag given for removal
            html_element = bs.find(tag_name)

            if html_element:
                html_content = html_element.decode_contents()
        else:
            # Remove any outer tag found
            html_element = bs.find()

            if html_element:
                html_content = html_element.decode_contents()

        return html_content

    @staticmethod
    def _try_parse_content_as_checklist_item(content: str) -> tuple[bool, bool | None, str]:
        empty_checkbox_pattern = re.compile(r'\[ ?\]\s*')
        checked_checkbox_pattern = re.compile(r'\[[xX]\]\s*')

        is_checked = None
        has_empty_checkbox = re.match(empty_checkbox_pattern, content)

        if has_empty_checkbox:
            content = re.sub(empty_checkbox_pattern, '', content)
            is_checked = False

        has_checked_checkbox = re.match(checked_checkbox_pattern, content)
        if has_checked_checkbox:
            content = re.sub(checked_checkbox_pattern, '', content)
            is_checked = True

        is_checklist_item = is_checked is not None

        return (
            is_checklist_item,
            is_checked,
            content
        )

    @classmethod
    def _marko_list_item_block_to_editor_block_data_dict(
            cls,
            marko_list_item_block: ListItem,
            parent_marko_list_block: List | None = None,
    ):
        list_item_editor_block_data_kwargs = {
            'items': [],
            'content': '',
            'meta': {},
        }

        # First determine if this item contains a nested list.
        # If it does, remove the list from the item's children (so the item content can be
        # properly rendered) and process it into editor_block_data if it does
        for i, child in enumerate(marko_list_item_block.children):
            if isinstance(child, List):
                nested_marko_list_block = marko_list_item_block.children.pop(i)
                for nested_child in nested_marko_list_block.children:
                    nested_list_item_editor_block_data_kwargs, _ = \
                        cls._marko_list_item_block_to_editor_block_data_dict(nested_child)
                    list_item_editor_block_data_kwargs['items'].append(nested_list_item_editor_block_data_kwargs)

                break

        # Marko wraps the text content in li when it renders a ListItem into html,
        # so we need to remove that, plus remove any leftover tags (e.g. if the content
        # in the li was a header)
        content = cls._remove_outer_html_tags(
            cls._remove_outer_html_tags(marko.render(marko_list_item_block), 'li')
        )

        is_checklist_item, is_checked, content = \
            cls._try_parse_content_as_checklist_item(content)

        if is_checklist_item:
            # Each editor list item block data tracks its checked state through an
            # item level meta
            list_item_editor_block_data_kwargs['meta']['checked'] = is_checked

        list_item_editor_block_data_kwargs['content'] = content

        list_editor_block_data_style = None
        if parent_marko_list_block:
            # We determine the entire list style from the top level list items for simplicity.
            # If parent_marko_list_block is present, it means we are processing the top level list.
            list_editor_block_data_style = ListEditorBlockDataStyle.UNORDERED
            if is_checklist_item:
                # The presence of checklist items takes priority over an ordered list style
                list_editor_block_data_style = ListEditorBlockDataStyle.CHECKLIST
            elif parent_marko_list_block.ordered:
                list_editor_block_data_style = ListEditorBlockDataStyle.ORDERED

        return list_item_editor_block_data_kwargs, list_editor_block_data_style

    @classmethod
    def _marko_block_to_editor_block_data_dict(cls, marko_block: BlockElement | Element):
        if isinstance(marko_block, BlankLine):
            return { 'text': '' }

        elif isinstance(marko_block, Paragraph):
            editor_block_text_string = cls._remove_outer_html_tags(marko.render(marko_block))
            return { 'text': editor_block_text_string }

        elif isinstance(marko_block, Heading):
            return {
                'text': cls._remove_outer_html_tags(marko.render(marko_block)),
                'level': marko_block.level,
            }

        elif isinstance(marko_block, List):
            list_editor_block_data_dict = {
                'items': [],
                'style': ListEditorBlockDataStyle.UNORDERED,
                'meta': {},
            }

            for child in marko_block.children:
                list_item_editor_block_data_dict, list_editor_block_data_style = \
                    cls._marko_list_item_block_to_editor_block_data_dict(child, marko_block)

                list_editor_block_data_dict['items'].append(list_item_editor_block_data_dict)
                list_editor_block_data_dict['style'] = list_editor_block_data_style

            return list_editor_block_data_dict

        else:
            logging.warning(
                f'Unsupported marko block type: {marko_block.__class__.__name__!r}. '
                f'Rendering content to html and adding to markdown as a basic paragraph block.'
            )
            return { 'text': marko.render(marko_block) }


    @classmethod
    def marko_block_to_markdown_string(cls, marko_block: BlockElement) -> str:
        return cls.html_to_markdown(marko.render(marko_block))

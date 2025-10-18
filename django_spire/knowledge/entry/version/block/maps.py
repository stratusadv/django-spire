from __future__ import annotations

from django_spire.knowledge.entry.version.block.blocks.list_block import ListItemBlock, \
    ListEditorBlockData
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.blocks.heading_block import \
    HeadingBlock, HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.blocks.sub_heading_block import \
    SubHeadingBlock
from django_spire.knowledge.entry.version.block.blocks.text_block import TextBlock, \
    TextEditorBlockData

ENTRY_BLOCK_MAP = {
    BlockTypeChoices.TEXT: TextBlock,
    BlockTypeChoices.HEADING: HeadingBlock,
    BlockTypeChoices.SUB_HEADING: SubHeadingBlock,
    BlockTypeChoices.LIST_ITEM: ListItemBlock,
}

EDITOR_BLOCK_DATA_MAP = {
    BlockTypeChoices.TEXT: TextEditorBlockData,
    BlockTypeChoices.HEADING: HeadingEditorBlockData,
    BlockTypeChoices.LIST: ListEditorBlockData,
}

from __future__ import annotations

from django_spire.knowledge.entry.version.block.blocks.list_block import ListItemBlock
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.blocks.heading_block import \
    HeadingBlock
from django_spire.knowledge.entry.version.block import entities
from django_spire.knowledge.entry.version.block.blocks.sub_heading_block import \
    SubHeadingBlock
from django_spire.knowledge.entry.version.block.blocks.text_block import TextBlock

ENTRY_BLOCK_MAP = {
    BlockTypeChoices.TEXT: TextBlock,
    BlockTypeChoices.HEADING: HeadingBlock,
    BlockTypeChoices.SUB_HEADING: SubHeadingBlock,
    BlockTypeChoices.LIST_ITEM: ListItemBlock,
}

EDITOR_BLOCK_DATA_MAP = {
    BlockTypeChoices.TEXT: entities.TextEditorBlockData,
    BlockTypeChoices.HEADING: entities.HeadingEditorBlockData,
    BlockTypeChoices.LIST: entities.ListEditorBlockData,
}

EDITOR_BLOCK_DATA_REVERSE_MAP = {
    entities.TextEditorBlockData: BlockTypeChoices.TEXT,
    entities.HeadingEditorBlockData: BlockTypeChoices.HEADING,
    entities.ListEditorBlockData: BlockTypeChoices.LIST,
}

LIST_BLOCK_DATA_META_MAP = {
    entities.ListEditorBlockDataStyle.ORDERED: entities.OrderedListItemMeta,
    entities.ListEditorBlockDataStyle.CHECKLIST: entities.ChecklistItemMeta,
    entities.ListEditorBlockDataStyle.UNORDERED: None,
}

LIST_BLOCK_DATA_REVERSE_META_MAP = {
    entities.OrderedListItemMeta: entities.ListEditorBlockDataStyle.ORDERED,
    entities.ChecklistItemMeta: entities.ListEditorBlockDataStyle.CHECKLIST,
    None: entities.ListEditorBlockDataStyle.UNORDERED,
}
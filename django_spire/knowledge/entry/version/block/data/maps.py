from __future__ import annotations

from django_spire.knowledge.entry.version.block.data import list_data
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.heading_data import \
    HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import \
    TextEditorBlockData


EDITOR_BLOCK_DATA_MAP = {
    BlockTypeChoices.TEXT: TextEditorBlockData,
    BlockTypeChoices.HEADING: HeadingEditorBlockData,
    BlockTypeChoices.LIST: list_data.ListEditorBlockData,
}


EDITOR_BLOCK_DATA_REVERSE_MAP = {
    TextEditorBlockData: BlockTypeChoices.TEXT,
    HeadingEditorBlockData: BlockTypeChoices.HEADING,
}


LIST_BLOCK_DATA_META_MAP = {
    list_data.ListEditorBlockDataStyle.ORDERED: list_data.OrderedListItemMeta,
    list_data.ListEditorBlockDataStyle.CHECKLIST: list_data.ChecklistItemMeta,
    list_data.ListEditorBlockDataStyle.UNORDERED: None,
}


LIST_BLOCK_DATA_REVERSE_META_MAP = {
    list_data.OrderedListItemMeta: list_data.ListEditorBlockDataStyle.ORDERED,
    list_data.ChecklistItemMeta: list_data.ListEditorBlockDataStyle.CHECKLIST,
    None: list_data.ListEditorBlockDataStyle.UNORDERED,
}
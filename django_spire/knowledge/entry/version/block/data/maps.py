from __future__ import annotations

from django_spire.knowledge.entry.version.block import entities
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.heading_data import \
    HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import \
    TextEditorBlockData


EDITOR_BLOCK_DATA_MAP = {
    BlockTypeChoices.TEXT: TextEditorBlockData,
    BlockTypeChoices.HEADING: HeadingEditorBlockData,
}


EDITOR_BLOCK_DATA_REVERSE_MAP = {
    TextEditorBlockData: BlockTypeChoices.TEXT,
    HeadingEditorBlockData: BlockTypeChoices.HEADING,
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
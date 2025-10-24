from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.list import choices, meta

LIST_BLOCK_DATA_META_MAP = {
    choices.ListEditorBlockDataStyle.ORDERED: meta.OrderedListItemMeta,
    choices.ListEditorBlockDataStyle.CHECKLIST: meta.ChecklistItemMeta,
    choices.ListEditorBlockDataStyle.UNORDERED: None,
}
LIST_BLOCK_DATA_REVERSE_META_MAP = {
    meta.OrderedListItemMeta: choices.ListEditorBlockDataStyle.ORDERED,
    meta.ChecklistItemMeta: choices.ListEditorBlockDataStyle.CHECKLIST,
    None: choices.ListEditorBlockDataStyle.UNORDERED,
}

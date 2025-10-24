from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.list.choices import (
    ListEditorBlockDataStyle,
)
from django_spire.knowledge.entry.version.block.data.list.meta import (
    ChecklistItemMeta,
    OrderedListItemMeta,
)


LIST_BLOCK_DATA_META_MAP = {
    ListEditorBlockDataStyle.ORDERED: OrderedListItemMeta,
    ListEditorBlockDataStyle.CHECKLIST: ChecklistItemMeta,
    ListEditorBlockDataStyle.UNORDERED: None,
}
LIST_BLOCK_DATA_REVERSE_META_MAP = {
    OrderedListItemMeta: ListEditorBlockDataStyle.ORDERED,
    ChecklistItemMeta: ListEditorBlockDataStyle.CHECKLIST,
    None: ListEditorBlockDataStyle.UNORDERED,
}

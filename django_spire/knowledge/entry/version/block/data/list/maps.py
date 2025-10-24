from __future__ import annotations

import django_spire.knowledge

LIST_BLOCK_DATA_META_MAP = {
    django_spire.knowledge.entry.version.block.data.list.choices.ListEditorBlockDataStyle.ORDERED: django_spire.knowledge.entry.version.block.data.list.meta.OrderedListItemMeta,
    django_spire.knowledge.entry.version.block.data.list.choices.ListEditorBlockDataStyle.CHECKLIST: django_spire.knowledge.entry.version.block.data.list.meta.ChecklistItemMeta,
    django_spire.knowledge.entry.version.block.data.list.choices.ListEditorBlockDataStyle.UNORDERED: None,
}
LIST_BLOCK_DATA_REVERSE_META_MAP = {
    django_spire.knowledge.entry.version.block.data.list.meta.OrderedListItemMeta: django_spire.knowledge.entry.version.block.data.list.choices.ListEditorBlockDataStyle.ORDERED,
    django_spire.knowledge.entry.version.block.data.list.meta.ChecklistItemMeta: django_spire.knowledge.entry.version.block.data.list.choices.ListEditorBlockDataStyle.CHECKLIST,
    None: django_spire.knowledge.entry.version.block.data.list.choices.ListEditorBlockDataStyle.UNORDERED,
}

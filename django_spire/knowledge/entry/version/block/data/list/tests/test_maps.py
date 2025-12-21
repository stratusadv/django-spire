from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.data.list.choices import ListEditorBlockDataStyle
from django_spire.knowledge.entry.version.block.data.list.maps import (
    LIST_BLOCK_DATA_META_MAP,
    LIST_BLOCK_DATA_REVERSE_META_MAP,
)
from django_spire.knowledge.entry.version.block.data.list.meta import (
    ChecklistItemMeta,
    OrderedListItemMeta,
)


class ListBlockDataMapTests(BaseTestCase):
    def test_meta_map_ordered(self):
        assert LIST_BLOCK_DATA_META_MAP[ListEditorBlockDataStyle.ORDERED] == OrderedListItemMeta

    def test_meta_map_checklist(self):
        assert LIST_BLOCK_DATA_META_MAP[ListEditorBlockDataStyle.CHECKLIST] == ChecklistItemMeta

    def test_meta_map_unordered(self):
        assert LIST_BLOCK_DATA_META_MAP[ListEditorBlockDataStyle.UNORDERED] is None

    def test_reverse_meta_map_ordered(self):
        assert LIST_BLOCK_DATA_REVERSE_META_MAP[OrderedListItemMeta] == ListEditorBlockDataStyle.ORDERED

    def test_reverse_meta_map_checklist(self):
        assert LIST_BLOCK_DATA_REVERSE_META_MAP[ChecklistItemMeta] == ListEditorBlockDataStyle.CHECKLIST

    def test_reverse_meta_map_unordered(self):
        assert LIST_BLOCK_DATA_REVERSE_META_MAP[None] == ListEditorBlockDataStyle.UNORDERED

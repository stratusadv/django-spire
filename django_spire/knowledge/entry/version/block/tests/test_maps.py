from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.heading_data import HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.list.data import ListEditorBlockData
from django_spire.knowledge.entry.version.block.data.maps import (
    EDITOR_JS_BLOCK_DATA_MAP,
    EDITOR_JS_BLOCK_DATA_REVERSE_MAP,
)
from django_spire.knowledge.entry.version.block.data.text_data import TextEditorBlockData


class EditorJsBlockDataMapTests(BaseTestCase):
    def test_map_contains_text(self):
        assert BlockTypeChoices.TEXT in EDITOR_JS_BLOCK_DATA_MAP
        assert EDITOR_JS_BLOCK_DATA_MAP[BlockTypeChoices.TEXT] == TextEditorBlockData

    def test_map_contains_heading(self):
        assert BlockTypeChoices.HEADING in EDITOR_JS_BLOCK_DATA_MAP
        assert EDITOR_JS_BLOCK_DATA_MAP[BlockTypeChoices.HEADING] == HeadingEditorBlockData

    def test_map_contains_list(self):
        assert BlockTypeChoices.LIST in EDITOR_JS_BLOCK_DATA_MAP
        assert EDITOR_JS_BLOCK_DATA_MAP[BlockTypeChoices.LIST] == ListEditorBlockData

    def test_reverse_map_contains_text(self):
        assert TextEditorBlockData in EDITOR_JS_BLOCK_DATA_REVERSE_MAP
        assert EDITOR_JS_BLOCK_DATA_REVERSE_MAP[TextEditorBlockData] == BlockTypeChoices.TEXT

    def test_reverse_map_contains_heading(self):
        assert HeadingEditorBlockData in EDITOR_JS_BLOCK_DATA_REVERSE_MAP
        assert EDITOR_JS_BLOCK_DATA_REVERSE_MAP[HeadingEditorBlockData] == BlockTypeChoices.HEADING

    def test_reverse_map_contains_list(self):
        assert ListEditorBlockData in EDITOR_JS_BLOCK_DATA_REVERSE_MAP
        assert EDITOR_JS_BLOCK_DATA_REVERSE_MAP[ListEditorBlockData] == BlockTypeChoices.LIST

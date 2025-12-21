from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.heading_data import HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.list.data import ListEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import TextEditorBlockData
from django_spire.knowledge.entry.version.block.tests.factories import create_test_version_block


class EntryVersionBlockModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.version_block = create_test_version_block()

    def test_editor_js_block_data_getter_text(self):
        self.version_block.type = BlockTypeChoices.TEXT
        self.version_block._block_data = {'text': 'Hello'}
        result = self.version_block.editor_js_block_data
        assert isinstance(result, TextEditorBlockData)
        assert result.text == 'Hello'

    def test_editor_js_block_data_getter_heading(self):
        self.version_block.type = BlockTypeChoices.HEADING
        self.version_block._block_data = {'text': 'Title', 'level': 1}
        result = self.version_block.editor_js_block_data
        assert isinstance(result, HeadingEditorBlockData)
        assert result.text == 'Title'
        assert result.level == 1

    def test_editor_js_block_data_getter_list(self):
        self.version_block.type = BlockTypeChoices.LIST
        self.version_block._block_data = {
            'style': 'unordered',
            'items': [{'content': 'Item 1', 'items': []}]
        }
        result = self.version_block.editor_js_block_data
        assert isinstance(result, ListEditorBlockData)

    def test_editor_js_block_data_setter(self):
        text_data = TextEditorBlockData(text='New text')
        self.version_block.editor_js_block_data = text_data
        assert self.version_block._block_data == {'text': 'New text'}
        assert 'New text' in self.version_block._text_data

    def test_update_editor_js_block_data_from_dict(self):
        self.version_block.type = BlockTypeChoices.TEXT
        self.version_block.update_editor_js_block_data_from_dict({'text': 'Updated'})
        assert self.version_block._block_data == {'text': 'Updated'}

    def test_render_to_text(self):
        self.version_block.type = BlockTypeChoices.TEXT
        self.version_block._block_data = {'text': 'Hello World'}
        result = self.version_block.render_to_text()
        assert 'Hello World' in result

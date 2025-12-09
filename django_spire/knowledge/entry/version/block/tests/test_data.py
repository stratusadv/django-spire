from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.data.heading_data import HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.list.choices import ListEditorBlockDataStyle
from django_spire.knowledge.entry.version.block.data.list.data import ListEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import TextEditorBlockData


class TextEditorBlockDataTests(BaseTestCase):
    def test_render_to_text(self):
        data = TextEditorBlockData(text='Hello World')
        result = data.render_to_text()
        assert 'Hello World' in result

    def test_render_to_text_with_html(self):
        data = TextEditorBlockData(text='<b>Bold</b> text')
        result = data.render_to_text()
        assert 'Bold' in result


class HeadingEditorBlockDataTests(BaseTestCase):
    def test_render_to_text_h1(self):
        data = HeadingEditorBlockData(text='Title', level=1)
        result = data.render_to_text()
        assert '# Title' in result

    def test_render_to_text_h2(self):
        data = HeadingEditorBlockData(text='Subtitle', level=2)
        result = data.render_to_text()
        assert '## Subtitle' in result

    def test_render_to_text_h3(self):
        data = HeadingEditorBlockData(text='Section', level=3)
        result = data.render_to_text()
        assert '### Section' in result


class ListEditorBlockDataTests(BaseTestCase):
    def test_render_to_text_unordered(self):
        data = ListEditorBlockData(
            style=ListEditorBlockDataStyle.UNORDERED,
            items=[
                {'content': 'Item 1', 'items': []},
                {'content': 'Item 2', 'items': []},
            ]
        )
        result = data.render_to_text()
        assert '- Item 1' in result
        assert '- Item 2' in result

    def test_render_to_text_ordered(self):
        data = ListEditorBlockData(
            style=ListEditorBlockDataStyle.ORDERED,
            meta={'start': 1},
            items=[
                {'content': 'First', 'items': [], 'meta': {'start': 1}},
                {'content': 'Second', 'items': [], 'meta': {'start': 1}},
            ]
        )
        result = data.render_to_text()
        assert '1. First' in result

    def test_render_to_text_checklist(self):
        data = ListEditorBlockData(
            style=ListEditorBlockDataStyle.CHECKLIST,
            items=[
                {'content': 'Done', 'items': [], 'meta': {'checked': True}},
                {'content': 'Not done', 'items': [], 'meta': {'checked': False}},
            ]
        )
        result = data.render_to_text()
        assert '[X] Done' in result
        assert '[ ] Not done' in result

    def test_render_to_text_nested(self):
        data = ListEditorBlockData(
            style=ListEditorBlockDataStyle.UNORDERED,
            items=[
                {
                    'content': 'Parent',
                    'items': [
                        {'content': 'Child', 'items': []}
                    ]
                },
            ]
        )
        result = data.render_to_text()
        assert 'Parent' in result
        assert 'Child' in result

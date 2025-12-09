from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.converters.markdown_converter import MarkdownConverter
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class MarkdownConverterTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.entry_version = create_test_entry_version()
        self.converter = MarkdownConverter(entry_version=self.entry_version)

    def test_convert_markdown_to_blocks_paragraph(self):
        markdown = 'This is a paragraph.'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        assert len(blocks) == 1
        assert blocks[0].type == BlockTypeChoices.TEXT

    def test_convert_markdown_to_blocks_heading(self):
        markdown = '# Heading 1'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        assert len(blocks) == 1
        assert blocks[0].type == BlockTypeChoices.HEADING

    def test_convert_markdown_to_blocks_multiple_headings(self):
        markdown = '# H1\n\n## H2\n\n### H3'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        heading_blocks = [b for b in blocks if b.type == BlockTypeChoices.HEADING]
        assert len(heading_blocks) == 3

    def test_convert_markdown_to_blocks_unordered_list(self):
        markdown = '- Item 1\n- Item 2\n- Item 3'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        list_blocks = [b for b in blocks if b.type == BlockTypeChoices.LIST]
        assert len(list_blocks) == 1

    def test_convert_markdown_to_blocks_ordered_list(self):
        markdown = '1. First\n2. Second\n3. Third'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        list_blocks = [b for b in blocks if b.type == BlockTypeChoices.LIST]
        assert len(list_blocks) == 1

    def test_convert_markdown_to_blocks_mixed_content(self):
        markdown = '# Title\n\nSome text.\n\n- List item'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        assert len(blocks) >= 3

    def test_convert_markdown_to_blocks_blank_lines(self):
        markdown = 'Para 1\n\n\n\nPara 2'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        assert len(blocks) >= 2

    def test_html_to_markdown(self):
        html = '<p>Hello <b>World</b></p>'
        result = MarkdownConverter.html_to_markdown(html)
        assert 'Hello' in result
        assert 'World' in result

    def test_convert_markdown_to_blocks_checklist(self):
        markdown = '- [ ] Todo\n- [x] Done'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        list_blocks = [b for b in blocks if b.type == BlockTypeChoices.LIST]
        assert len(list_blocks) == 1

    def test_convert_markdown_to_blocks_nested_list(self):
        markdown = '- Parent\n  - Child'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        list_blocks = [b for b in blocks if b.type == BlockTypeChoices.LIST]
        assert len(list_blocks) == 1

    def test_block_ordering(self):
        markdown = '# H1\n\nParagraph\n\n- List'
        blocks = self.converter.convert_markdown_to_blocks(markdown)
        for i, block in enumerate(blocks):
            assert block.order == i

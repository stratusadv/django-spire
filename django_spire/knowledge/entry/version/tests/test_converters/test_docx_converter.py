from __future__ import annotations

import time

from unittest.mock import MagicMock, patch

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.consts import MARKDOWN_AI_CHUNK_SIZE
from django_spire.knowledge.entry.version.converters.docx_converter import DocxConverter
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class DocxConverterTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_entry_version = create_test_entry_version()

    @patch(
        'django_spire.knowledge.entry.version.converters.docx_converter.'
        'MarkdownFormatLlmBot.process'
    )
    def test_improve_markdown_structure_concurrent_execution(
        self,
        mock_process_method: MagicMock
    ):
        def slow_process(markdown_content: str):
            time.sleep(0.1)
            return markdown_content

        mock_process_method.side_effect = slow_process
        docx_converter = DocxConverter(entry_version=self.test_entry_version)
        mock_chunks = [
            f'{x}' + ''.join('x' for _ in range(MARKDOWN_AI_CHUNK_SIZE - 1))
            for x in range(1, 4)
        ]
        start_time = time.time()
        improved_markdown = docx_converter.improve_markdown_structure(
            markdown_content=''.join(mock_chunks)
        )
        end_time = time.time()
        assert end_time - start_time < 0.3
        assert mock_process_method.call_count == 3
        assert improved_markdown == ''.join(mock_chunks)

    @patch(
        'django_spire.knowledge.entry.version.converters.docx_converter.'
        'MarkdownFormatLlmBot.process'
    )
    def test_improve_markdown_structure_returns_content(
        self,
        mock_process_method: MagicMock
    ):
        mock_process_method.side_effect = lambda x: x
        docx_converter = DocxConverter(entry_version=self.test_entry_version)

        markdown = 'a' * MARKDOWN_AI_CHUNK_SIZE + 'b' * MARKDOWN_AI_CHUNK_SIZE
        result = docx_converter.improve_markdown_structure(markdown_content=markdown)

        assert len(result) == len(markdown)
        assert mock_process_method.call_count == 2

    @patch(
        'django_spire.knowledge.entry.version.converters.docx_converter.'
        'MarkdownFormatLlmBot.process'
    )
    def test_improve_markdown_structure_handles_exception(
        self,
        mock_process_method: MagicMock
    ):
        original_chunk = 'x' * MARKDOWN_AI_CHUNK_SIZE
        mock_process_method.side_effect = Exception('Test error')
        docx_converter = DocxConverter(entry_version=self.test_entry_version)

        result = docx_converter.improve_markdown_structure(markdown_content=original_chunk)
        assert result == original_chunk

    @patch(
        'django_spire.knowledge.entry.version.converters.docx_converter.'
        'MarkdownFormatLlmBot.process'
    )
    def test_improve_markdown_structure_single_chunk(
        self,
        mock_process_method: MagicMock
    ):
        mock_process_method.side_effect = lambda x: x
        docx_converter = DocxConverter(entry_version=self.test_entry_version)

        short_content = 'short content'
        result = docx_converter.improve_markdown_structure(markdown_content=short_content)

        assert result == short_content
        assert mock_process_method.call_count == 1

from __future__ import annotations

import time

from unittest.mock import MagicMock, patch

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.constants import MARKDOWN_AI_CHUNK_SIZE
from django_spire.knowledge.entry.version.converters.docx_converter import DocxConverter

from django_spire.knowledge.entry.version.tests.factories import \
    create_test_entry_version


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
        self.assertLess(end_time - start_time, 0.3)
        self.assertEqual(mock_process_method.call_count, 3)
        self.assertEqual(improved_markdown, ''.join(mock_chunks))

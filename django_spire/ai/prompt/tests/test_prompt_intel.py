from __future__ import annotations

from django_spire.ai.prompt.intel import DandyPromptPythonFileIntel, TextToMarkdownIntel
from django_spire.core.tests.test_cases import BaseTestCase


class DandyPromptPythonFileIntelTests(BaseTestCase):
    def test_dandy_prompt_python_file_intel_creation(self) -> None:
        intel = DandyPromptPythonFileIntel(
            source_code='print("hello")',
            file_name='test.py'
        )

        assert intel.source_code == 'print("hello")'
        assert intel.file_name == 'test.py'

    def test_dandy_prompt_python_file_intel_empty_source(self) -> None:
        intel = DandyPromptPythonFileIntel(
            source_code='',
            file_name='empty.py'
        )

        assert intel.source_code == ''

    def test_dandy_prompt_python_file_intel_long_source(self) -> None:
        long_source = 'x = 1\n' * 1000
        intel = DandyPromptPythonFileIntel(
            source_code=long_source,
            file_name='long.py'
        )

        assert intel.source_code == long_source


class TextToMarkdownIntelTests(BaseTestCase):
    def test_text_to_markdown_intel_creation(self) -> None:
        intel = TextToMarkdownIntel(
            markdown_content='# Hello World',
            file_name='test.md'
        )

        assert intel.markdown_content == '# Hello World'
        assert intel.file_name == 'test.md'

    def test_text_to_markdown_intel_empty_content(self) -> None:
        intel = TextToMarkdownIntel(
            markdown_content='',
            file_name='empty.md'
        )

        assert intel.markdown_content == ''

    def test_text_to_markdown_intel_complex_markdown(self) -> None:
        complex_md = """
            # Title

            ## Section 1

            - Item 1
            - Item 2

            ```python
            print("code")
            ```
        """

        intel = TextToMarkdownIntel(
            markdown_content=complex_md,
            file_name='complex.md'
        )

        assert intel.markdown_content == complex_md

    def test_text_to_markdown_intel_model_dump(self) -> None:
        intel = TextToMarkdownIntel(
            markdown_content='Test',
            file_name='test.md'
        )

        dump = intel.model_dump()

        assert 'markdown_content' in dump
        assert 'file_name' in dump

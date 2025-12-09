from __future__ import annotations

from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import TYPE_CHECKING

from markitdown import MarkItDown

from django_spire.knowledge.entry.version.consts import MARKDOWN_AI_CHUNK_SIZE
from django_spire.knowledge.entry.version.converters.converter import BaseConverter
from django_spire.knowledge.entry.version.converters.markdown_converter import MarkdownConverter
from django_spire.knowledge.entry.version.intelligence.bots.markdown_format_llm_bot import MarkdownFormatLlmBot

if TYPE_CHECKING:
    from django_spire.file.models import File
    from django_spire.knowledge.entry.version.block import models


class DocxConverter(BaseConverter):
    """Converts DocX content to a list of EntryVersionBlocks using Markitdown, AI and
    the MarkdownConverter.

    For more info on Markitdown:
    https://github.com/microsoft/markitdown
    """

    def convert_file_to_blocks(self, file: File) -> list[models.EntryVersionBlock]:
        markitdown = MarkItDown()
        markdown_result = markitdown.convert(file.file.url)
        markdown_content = markdown_result.markdown

        markdown_converter = MarkdownConverter(entry_version=self.entry_version)
        return markdown_converter.convert_markdown_to_blocks(
            markdown_content=self.improve_markdown_structure(markdown_content)
        )

    @staticmethod
    def improve_markdown_structure(markdown_content: str) -> str:
        markdown_content_chunks = [
            markdown_content[i: i + MARKDOWN_AI_CHUNK_SIZE]
            for i in range(0, len(markdown_content), MARKDOWN_AI_CHUNK_SIZE)
        ]

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for idx, chunk in enumerate(markdown_content_chunks):
                future = executor.submit(
                    MarkdownFormatLlmBot().process,
                    markdown_content=chunk
                )
                future.index = idx
                futures.append(future)

            improved_chunks = {}
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    improved_chunks[future.index] = result
                except Exception:
                    improved_chunks[future.index] = markdown_content_chunks[future.index]

        sorted_improved_chunks = sorted(improved_chunks.items(), key=lambda x: x[0])
        return ''.join(chunk[1] for chunk in sorted_improved_chunks)

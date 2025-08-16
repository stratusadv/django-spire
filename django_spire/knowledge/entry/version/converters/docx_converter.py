from __future__ import annotations

from collections import defaultdict
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import TYPE_CHECKING

from markitdown import MarkItDown

from django_spire.knowledge.entry.version.constants import MARKDOWN_AI_CHUNK_SIZE
from django_spire.knowledge.entry.version.converters.converter import \
    BaseConverter
from django_spire.knowledge.entry.version.block import models
from django_spire.knowledge.entry.version.converters.markdown_converter import \
    MarkdownConverter
from django_spire.knowledge.entry.version.intelligence.bots.markdown_format_llm_bot import \
    MarkdownFormatLlmBot

if TYPE_CHECKING:
    from django_spire.file.models import File


class DocxConverter(BaseConverter):
    """Converts a DocX content to a list of EntryVersionBlocks using Markitdown, AI and
    the MarkdownConverter.

    For more info on Markitdown:
    https://github.com/microsoft/markitdown
    """

    def convert_file_to_blocks(self, file: File) -> list[models.EntryVersionBlock]:
        markitdown = MarkItDown()
        markdown_result = markitdown.convert(file.file.path)
        markdown_content = markdown_result.markdown

        markdown_content_chunks = [
            markdown_content[i: i + MARKDOWN_AI_CHUNK_SIZE]
            for i in range(0, len(markdown_content), MARKDOWN_AI_CHUNK_SIZE)
        ]

        markdown_format_bot = MarkdownFormatLlmBot()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for idx, chunk in enumerate(markdown_content_chunks):
                future = executor.submit(
                    markdown_format_bot.process,
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

        markdown_converter = MarkdownConverter(entry_version=self.entry_version)
        blocks = markdown_converter.convert_markdown_to_blocks(
            markdown_content=''.join(improved_chunks.values())
        )

        return blocks

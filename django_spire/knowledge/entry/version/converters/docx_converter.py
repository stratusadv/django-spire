from __future__ import annotations

from typing import TYPE_CHECKING

from markitdown import MarkItDown

from django_spire.knowledge.entry.version.converters.converter import \
    BaseConverter
from django_spire.knowledge.entry.version.block import models

if TYPE_CHECKING:
    from django_spire.file.models import File


class DocxConverter(BaseConverter):
    """Converts a DocX content to a list of EntryVersionBlocks using Markitdown, AI and
    the MarkdownConverter.

    For more info on Markitdown:
    https://github.com/microsoft/markitdown
    """

    def convert_file_to_blocks(self, file: File) -> list[models.EntryVersionBlock]:
        blocks = []

        markitdown = MarkItDown()
        markdown_content = markitdown.convert(file.file.path)
        a = 1

        return blocks

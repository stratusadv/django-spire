from __future__ import annotations

from django_spire.knowledge.entry.version.converters.docx_converter import DocxConverter
from django_spire.knowledge.entry.version.converters.markdown_converter import MarkdownConverter


FILE_TYPE_CONVERTER_MAP = {
    'md': MarkdownConverter,
    'docx': DocxConverter
}

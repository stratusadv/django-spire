from __future__ import annotations

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.heading_data import \
    HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.list.data import \
    ListEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import \
    TextEditorBlockData


EDITOR_JS_BLOCK_DATA_MAP = {
    BlockTypeChoices.TEXT: TextEditorBlockData,
    BlockTypeChoices.HEADING: HeadingEditorBlockData,
    BlockTypeChoices.LIST: ListEditorBlockData,
}


EDITOR_JS_BLOCK_DATA_REVERSE_MAP = {
    value: key for key, value in EDITOR_JS_BLOCK_DATA_MAP.items()
}

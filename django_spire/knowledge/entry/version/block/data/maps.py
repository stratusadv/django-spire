from __future__ import annotations

import django_spire.knowledge.entry.version.block.data.list.choices
import django_spire.knowledge.entry.version.block.data.list.data
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.heading_data import \
    HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import \
    TextEditorBlockData


EDITOR_BLOCK_DATA_MAP = {
    BlockTypeChoices.TEXT: TextEditorBlockData,
    BlockTypeChoices.HEADING: HeadingEditorBlockData,
    BlockTypeChoices.LIST: django_spire.knowledge.entry.version.block.data.list.data.ListEditorBlockData,
}


EDITOR_BLOCK_DATA_REVERSE_MAP = {
    TextEditorBlockData: BlockTypeChoices.TEXT,
    HeadingEditorBlockData: BlockTypeChoices.HEADING,
}

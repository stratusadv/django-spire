from enum import Enum

from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.editor.blocks.heading_block import HeadingBlock
from django_spire.knowledge.entry.editor.blocks.sub_heading_block import SubHeadingBlock
from django_spire.knowledge.entry.editor.blocks.text_block import TextBlock

ENTRY_BLOCK_MAP = {
    BlockTypeChoices.TEXT: TextBlock,
    BlockTypeChoices.HEADING: HeadingBlock,
    BlockTypeChoices.SUB_HEADING: SubHeadingBlock,
}

from django_spire.knowledge.entry.version.block.blocks.list_block import ListItemBlock
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.blocks.heading_block import HeadingBlock
from django_spire.knowledge.entry.version.block.blocks.sub_heading_block import \
    SubHeadingBlock
from django_spire.knowledge.entry.version.block.blocks.text_block import TextBlock


ENTRY_BLOCK_MAP = {
    BlockTypeChoices.TEXT: TextBlock,
    BlockTypeChoices.HEADING: HeadingBlock,
    BlockTypeChoices.SUB_HEADING: SubHeadingBlock,
    BlockTypeChoices.LIST_ITEM: ListItemBlock,
}

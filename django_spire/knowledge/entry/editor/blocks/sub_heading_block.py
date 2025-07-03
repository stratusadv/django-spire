from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.editor.blocks.block import BaseBlock


class SubHeadingBlock(BaseBlock):
    value: str
    _type: BlockTypeChoices = BlockTypeChoices.SUB_HEADING

    def render_to_text(self) -> str:
        return f'{self.value}\n'
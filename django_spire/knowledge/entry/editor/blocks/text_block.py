from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.editor.blocks.block import BaseBlock


class TextBlock(BaseBlock):
    value: str
    _type: BlockTypeChoices = BlockTypeChoices.TEXT

    def render_to_text(self) -> str:
        return f'{self.value}\n'
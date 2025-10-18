from __future__ import annotations

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock, \
    BaseEditorBlockData


class TextBlock(BaseBlock):
    value: str
    type: BlockTypeChoices = BlockTypeChoices.TEXT
    detail_template: str = 'django_spire/knowledge/entry/version/block/detail/component/text_component.html'
    update_template: str = 'django_spire/knowledge/entry/version/block/update/component/text_component.html'

    def render_to_text(self) -> str:
        return f'{self.value}\n'

class TextEditorBlockData(BaseEditorBlockData):
    text: str

    def render_to_text(self) -> str:
        return f'{self.text}\n'
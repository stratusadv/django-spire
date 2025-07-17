from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.editor.blocks.block import BaseBlock, EditBlock


class TextBlock(BaseBlock, EditBlock):
    value: str
    _type: BlockTypeChoices = BlockTypeChoices.TEXT
    edit_template: str = 'django_spire/knowledge/entry/editor/block/component/edit_text_component.html'

    def render_to_text(self) -> str:
        return f'{self.value}\n'

    def render_to_html(self) -> str:
        return f'<span class="fs-6">{self.value}</span>\n'

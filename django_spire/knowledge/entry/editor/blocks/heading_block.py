from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.editor.blocks.block import BaseBlock


class HeadingBlock(BaseBlock):
    value: str
    type: BlockTypeChoices = BlockTypeChoices.HEADING
    display_template: str = 'django_spire/knowledge/entry/editor/block/display/component/heading_component.html'
    update_template: str = 'django_spire/knowledge/entry/editor/block/update/component/heading_component.html'

    def render_to_text(self) -> str:
        return f'{self.value}\n'

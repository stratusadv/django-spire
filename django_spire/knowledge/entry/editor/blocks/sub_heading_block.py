from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.editor.blocks.block import BaseBlock


class SubHeadingBlock(BaseBlock):
    value: str
    type: BlockTypeChoices = BlockTypeChoices.SUB_HEADING
    display_template: str = 'django_spire/knowledge/entry/editor/block/display/component/sub_heading_component.html'
    update_template: str = 'django_spire/knowledge/entry/editor/block/update/component/update_text_component.html'

    def render_to_text(self) -> str:
        return f'{self.value}\n'

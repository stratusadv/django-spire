from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock


class SubHeadingBlock(BaseBlock):
    value: str
    type: BlockTypeChoices = BlockTypeChoices.SUB_HEADING
    detail_template: str = 'django_spire/knowledge/entry/version/block/detail/component/sub_heading_component.html'
    update_template: str = 'django_spire/knowledge/entry/version/block/update/component/sub_heading_component.html'

    def render_to_text(self) -> str:
        return f'{self.value}\n'

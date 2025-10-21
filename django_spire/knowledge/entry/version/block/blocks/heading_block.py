from __future__ import annotations

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock


# Keeping this and other BaseBlock subclasses around until we confirm we don't need to do data conversion
class HeadingBlock(BaseBlock):
    value: str
    type: BlockTypeChoices = BlockTypeChoices.HEADING
    detail_template: str = 'django_spire/knowledge/entry/version/block/detail/component/heading_component.html'
    update_template: str = 'django_spire/knowledge/entry/version/block/update/component/heading_component.html'

    def render_to_text(self) -> str:
        return f'{self.value}\n'
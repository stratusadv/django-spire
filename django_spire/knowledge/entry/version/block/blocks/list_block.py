from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.constants import SPACES_PER_INDENT

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class ListItemBlock(BaseBlock):
    value: str
    type: BlockTypeChoices = BlockTypeChoices.LIST_ITEM
    detail_template: str = 'django_spire/knowledge/entry/version/block/detail/component/list_item_component.html'
    update_template: str = 'django_spire/knowledge/entry/version/block/update/component/list_item_component.html'
    indent_level: int = 0
    bullet: str = '-'
    ordered: bool = False

    def render_to_text(self) -> str:
        indent = ' ' * self.indent_level * SPACES_PER_INDENT
        return f'{indent}{self.bullet} {self.value}\n'

    def to_dict(self, version_block: EntryVersionBlock):
        return super().to_dict(version_block) | {
            'indent_level': self.indent_level,
            'bullet': self.bullet,
            'ordered': self.ordered,
        }

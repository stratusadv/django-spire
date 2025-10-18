from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from numpy.f2py.f2py2e import get_prefix
from pydantic import BaseModel

from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock, \
    BaseEditorBlockData
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


class ListEditorBlockData(BaseEditorBlockData):
    style: ListEditorBlockDataStyle
    meta: BaseItemMeta | None = None
    items: list[ListItemEditorBlockData] = []

    def render_to_text(self) -> str:
        render_string = ''
        for i, item in enumerate(self.items):
            render_string += item.render_to_text(self.style, 0, i)

        return render_string


class ListItemEditorBlockData(BaseEditorBlockData):
    content: str
    meta: BaseItemMeta | None = None
    items: list[ListItemEditorBlockData] = []
    ordered: bool

    def get_prefix(
            self,
            style: ListEditorBlockDataStyle,
            indent_level: int,
            index = None
    ):
        prefix = ' ' * indent_level * SPACES_PER_INDENT

        if style == ListEditorBlockDataStyle.ORDERED:
            index = index or 0
            start = self.meta.start or 1
            prefix += f'{start + index}.'

        elif style == ListEditorBlockDataStyle.CHECKLIST:
            prefix += f'[{"X" if self.meta.checked else " "}]'

        else:
            prefix += '-'

        return prefix

    def render_to_text(
        self,
        style: ListEditorBlockDataStyle,
        indent_level: int,
        index: int
    ) -> str:
        prefix = self.get_prefix(style, indent_level, index)
        render_string = f'{prefix} {self.content}\n'
        for i, item in enumerate(self.items):
            render_string += item.render_to_text(style, indent_level + 1, i)

        return render_string


class ListEditorBlockDataStyle(enum.Enum):
    UNORDERED = 'unordered'
    ORDERED = 'ordered'
    CHECKLIST = 'checklist'


class BaseItemMeta(BaseModel):
    pass


class ChecklistItemMeta(BaseItemMeta):
    checked: bool


class OrderedListCounterType(enum.Enum):
    NUMERIC = 'numeric'
    UPPER_ROMAN = 'upper-roman'
    LOWER_ROMAN = 'lower-roman'
    UPPER_ALPHA = 'upper-alpha'
    LOWER_ALPHA = 'lower-alpha'


class OrderedListItemMeta(BaseItemMeta):
    start: int | None = None
    counterType: OrderedListCounterType | None = None


class UnorderedListItemMeta(BaseItemMeta):
    pass

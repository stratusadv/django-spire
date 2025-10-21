from __future__ import annotations

import enum

from pydantic import BaseModel

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.constants import SPACES_PER_INDENT


class EditorBlock(BaseModel):
    """
    Represents an individual block within the EditorJS save output.

    This class provides a structured representation of a block that is formatted from the
    EditorJS save output.
    It includes attributes to store information about the block's type,
    order within the editor, additional data, and any optional customizations or
    "tunes" that may apply to the block.

    Attributes:
        order (int): The order or position of the block within a sequence of blocks.
        type (BlockTypeChoices): The type of the block, (e.g., text, heading, list).
        data (dict): The data object for the block. The structure of this depends on the block type (see 'BaseEditorBlockData' and subclasses).
        tunes (dict | None): Customizations or additional configurations for the
            block, which may include optional parameters.
    """
    order: int
    type: BlockTypeChoices
    data: dict
    tunes: dict | None


# BASE
class BaseEditorBlockData(BaseModel):
    """
    This class serves as a foundational abstract model for EditorJS tool data objects.

    Note that it does not represent the top level editor block itself,
    but rather the data that is stored within it.
    For the editor block itself, see 'EditorBlock', whose 'data' dict attribute's structure
    must conform to the associated BaseEditorBlockData subclass.
    See https://editorjs.io/getting-started/#tools-installation for a
    list of EditorJS and their associated data models.
    """

    def render_to_text(self) -> str:
        """
        Renders the content to text format.

        This method should be implemented in a subclass to define how the
        content will be rendered into a string. It is meant to be overridden and
        raises a NotImplementedError by default.

        This method is mainly used for providing knowledge base
        content in a digestible format for the AI Chat's LLM connector.

        Returns:
            str: The rendered text output.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError


# TEXT
class TextEditorBlockData(BaseEditorBlockData):
    text: str

    def render_to_text(self) -> str:
        return f'{self.text}\n'


# HEADING
class HeadingEditorBlockData(BaseEditorBlockData):
    text: str
    level: int

    def render_to_text(self) -> str:
        return f'{"#" * self.level} {self.text}\n'


# LIST
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

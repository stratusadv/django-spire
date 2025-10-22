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
    order within the editor, content data, and any optional customizations or
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
from __future__ import annotations

from pydantic import BaseModel


class BaseEditorBlockData(BaseModel):
    """
    This class serves as a foundational abstract model for EditorJS tool data objects.

    Note that it does not represent the top level editor block itself,
    but rather the data that is stored within it.
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

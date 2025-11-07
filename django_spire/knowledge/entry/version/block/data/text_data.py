from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.data import BaseEditorJsBlockData


class TextEditorBlockData(BaseEditorJsBlockData):
    text: str

    def render_to_text(self) -> str:
        from django_spire.knowledge.entry.version.converters.markdown_converter import \
            MarkdownConverter

        return f'{MarkdownConverter.html_to_markdown(self.text)}\n'

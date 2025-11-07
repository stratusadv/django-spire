from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.data import BaseEditorJsBlockData


class HeadingEditorBlockData(BaseEditorJsBlockData):
    text: str
    level: int

    def render_to_text(self) -> str:
        from django_spire.knowledge.entry.version.converters.markdown_converter import \
            MarkdownConverter

        text = MarkdownConverter.html_to_markdown(self.text)
        return f'{"#" * self.level} {text}\n'

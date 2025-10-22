from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.data import BaseEditorBlockData


class TextEditorBlockData(BaseEditorBlockData):
    text: str

    def render_to_text(self) -> str:
        return f'{self.text}\n'

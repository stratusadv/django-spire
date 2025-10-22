from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.data import BaseEditorBlockData


class HeadingEditorBlockData(BaseEditorBlockData):
    text: str
    level: int

    def render_to_text(self) -> str:
        return f'{"#" * self.level} {self.text}\n'

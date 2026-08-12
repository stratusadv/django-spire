from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.data import BaseEditorJsBlockData


class CodeEditorBlockData(BaseEditorJsBlockData):
    code: str

    def render_to_text(self) -> str:
        return f'```\n{self.code}\n```\n'

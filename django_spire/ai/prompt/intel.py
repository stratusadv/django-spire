from __future__ import annotations

from dandy.intel import BaseIntel


class DandyPromptPythonFileIntel(BaseIntel):
    source_code: str
    file_name: str


class TextToMarkdownIntel(BaseIntel):
    markdown_content: str
    file_name: str

from __future__ import annotations

from dandy.intel import BaseIntel


class SystemPromptResultIntel(BaseIntel):
    result: str




class SystemPromptIntel(BaseIntel):
    role: str
    task: str
    guidelines: list[str]
    output_format: str

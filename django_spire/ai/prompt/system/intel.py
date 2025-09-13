from __future__ import annotations

from dandy.intel import BaseIntel


class SystemPromptResultIntel(BaseIntel):
    result: str


class SystemPromptIntel(BaseIntel):
    role: str
    task: str
    context: str
    guidelines: str
    expected_user_input: str
    output_format: str
    constraints: str

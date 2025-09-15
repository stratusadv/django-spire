from __future__ import annotations

from dandy.intel import BaseIntel


class PromptTestingIntel(BaseIntel):
    result: str


class PromptTuningIntel(BaseIntel):
    prompt: str

from __future__ import annotations

from dandy import BaseIntel


class AnswerIntel(BaseIntel):
    answer: str
    is_knowledge_based: bool

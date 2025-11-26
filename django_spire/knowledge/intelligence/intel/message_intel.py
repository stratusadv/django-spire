from __future__ import annotations

from django_spire.ai.chat.message_intel import BaseMessageIntel
from django_spire.knowledge.intelligence.intel.answer_intel import AnswerIntel
from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel


class KnowledgeMessageIntel(BaseMessageIntel):
    _template: str = 'django_spire/knowledge/message/knowledge_message_intel.html'
    answer_intel: AnswerIntel
    entries_intel: EntriesIntel

    def render_to_str(self) -> str:
        return self.answer_intel.answer

from __future__ import annotations

from django_spire.ai.chat.message_intel import BaseMessageIntel
from django_spire.knowledge.intelligence.intel.knowledge_answer_intel import KnowledgeAnswerIntel


class KnowledgeMessageIntel(BaseMessageIntel):
    _template: str = 'django_spire/knowledge/message/knowledge_message_intel.html'
    knowledge_answer_intel: KnowledgeAnswerIntel

    def render_to_str(self) -> str:
        return self.knowledge_answer_intel.answer

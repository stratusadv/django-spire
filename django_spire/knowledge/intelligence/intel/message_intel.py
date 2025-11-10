from __future__ import annotations

from django_spire.ai.chat.message_intel import BaseMessageIntel
from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel


class KnowledgeMessageIntel(BaseMessageIntel):
    _template: str = 'django_spire/knowledge/message/knowledge_message_intel.html'
    body: str
    entries_intel: EntriesIntel

    def content_to_str(self) -> str:
        return self.body

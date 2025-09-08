from django_spire.ai.chat.message_intel import BaseMessageIntel


class KnowledgeMessageIntel(BaseMessageIntel):
    _template: str = 'django_spire/knowledge/message/knowledge_message_intel.html'
    body: str

    def content_to_str(self) -> str:
        return self.body

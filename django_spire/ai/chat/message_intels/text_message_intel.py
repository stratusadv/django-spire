from django_spire.ai.chat.message_intels import BaseMessageIntel


class TextMessageIntel(BaseMessageIntel):
    _template = 'django_spire/ai/chat/message_intels/text_message_intel.html'
    text: str

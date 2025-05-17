from dandy.intel import BaseIntel
from django.template.loader import render_to_string
from pydantic import PrivateAttr


class BaseMessageIntel(BaseIntel):
    _template: str = PrivateAttr(default_factory=str)

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls._template is None or cls._template == '':
            raise ValueError(f'{cls.__name__}._template must be set')

    def render_to_string(self, context_data: dict | None = None):
        return render_to_string(
            template_name=self._template,
            context={**self.model_dump(), **(context_data or {})},
        )


class DefaultMessageIntel(BaseMessageIntel):
    _template = 'django_spire/ai/chat/messages/default_message.html'
    text: str
from dandy.intel import BaseIntel
from django.template.loader import render_to_string
from pydantic import PrivateAttr


class BaseMessageIntel(BaseIntel):
    template: str

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls.template is None or cls.template == '':
            raise ValueError(f'{cls.__name__}._template must be set')

    def render_to_string(self, context_data: dict | None = None):
        return render_to_string(
            template_name=self._template,
            context={**self.model_dump(), **(context_data or {})},
        )



class DefaultMessageIntel(BaseMessageIntel):
    template: str = 'django_spire/ai/chat/message/default_message.html'
    text: str
from abc import abstractmethod, ABC

from dandy.intel import BaseIntel
from django.template.loader import render_to_string


class BaseMessageIntel(BaseIntel, ABC):
    _template: str

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls._template is None or cls._template == '':
            raise ValueError(f'{cls.__module__}.{cls.__qualname____}._template must be set')

    @abstractmethod
    def content_to_str(self) -> str:
        raise NotImplementedError

    def render_to_string(self, context_data: dict | None = None):
        return render_to_string(
            template_name=self._template,
            context={**self.model_dump(), **(context_data or {})},
        )

    @property
    def template(self) -> str:
        return self._template


class DefaultMessageIntel(BaseMessageIntel):
    _template: str = 'django_spire/ai/chat/message/default_message.html'
    text: str

    def content_to_str(self):
        return self.text
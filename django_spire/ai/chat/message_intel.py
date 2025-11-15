from __future__ import annotations

from abc import ABC, abstractmethod

from dandy import BaseIntel
from django.template.loader import render_to_string


class BaseMessageIntel(BaseIntel, ABC):
    _template: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        template = cls.__dict__.get('_template')

        if template is None and hasattr(cls, '__private_attributes__'):
            private_attr = cls.__private_attributes__.get('_template')

            if private_attr and hasattr(private_attr, 'default'):
                template = private_attr.default

        if not template:
            message = f'{cls.__module__}.{cls.__qualname__}._template must be set'
            raise ValueError(message)

    @abstractmethod
    def render_to_str(self) -> str:
        raise NotImplementedError

    def render_template_to_str(self, context_data: dict | None = None):
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

    def render_to_str(self) -> str:
        return self.text

from __future__ import annotations

import pytest

from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.core.tests.test_cases import BaseTestCase


class CustomMessageIntel(BaseMessageIntel):
    _template: str = 'django_spire/ai/chat/message/default_message.html'
    text: str
    extra_data: str = 'Extra'

    def render_to_str(self) -> str:
        return f'{self.text} - {self.extra_data}'


class TestMessageIntel(BaseTestCase):
    def test_default_message_intel_has_template(self) -> None:
        intel = DefaultMessageIntel(text='Test')
        assert intel.template == 'django_spire/ai/chat/message/default_message.html'

    def test_default_message_intel_render_to_str(self) -> None:
        intel = DefaultMessageIntel(text='Hello World')
        result = intel.render_to_str()

        assert result == 'Hello World'

    def test_custom_message_intel_render_to_str(self) -> None:
        intel = CustomMessageIntel(text='Test', extra_data='Custom')
        result = intel.render_to_str()

        assert result == 'Test - Custom'

    def test_render_template_to_str_renders_django_template(self) -> None:
        intel = DefaultMessageIntel(text='Hello')
        result = intel.render_template_to_str()

        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_template_to_str_with_context(self) -> None:
        intel = DefaultMessageIntel(text='Test')
        result = intel.render_template_to_str(context_data={'extra': 'data'})

        assert isinstance(result, str)

    def test_template_property(self) -> None:
        intel = DefaultMessageIntel(text='Test')

        assert intel.template == intel._template

    def test_message_intel_raises_without_template(self) -> None:
        with pytest.raises(ValueError):
            class NoTemplateIntel(BaseMessageIntel):
                _template = None

                def render_to_str(self) -> str:
                    return 'test'

    def test_message_intel_raises_with_empty_template(self) -> None:
        with pytest.raises(ValueError):
            class EmptyTemplateIntel(BaseMessageIntel):
                _template = ''

                def render_to_str(self) -> str:
                    return 'test'

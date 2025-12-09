from __future__ import annotations

import pytest

from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.core.tests.test_cases import BaseTestCase


class CustomMessageIntel(BaseMessageIntel):
    _template: str = 'django_spire/ai/chat/message/default_message.html'
    extra_data: str = 'Extra'
    text: str

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

    def test_default_message_intel_model_dump(self) -> None:
        intel = DefaultMessageIntel(text='Test text')
        dump = intel.model_dump()

        assert 'text' in dump
        assert dump['text'] == 'Test text'

    def test_custom_message_intel_default_extra_data(self) -> None:
        intel = CustomMessageIntel(text='Test')

        assert intel.extra_data == 'Extra'

    def test_default_message_intel_empty_text(self) -> None:
        intel = DefaultMessageIntel(text='')
        result = intel.render_to_str()

        assert result == ''

    def test_default_message_intel_long_text(self) -> None:
        long_text = 'A' * 10000
        intel = DefaultMessageIntel(text=long_text)
        result = intel.render_to_str()

        assert result == long_text
        assert len(result) == 10000

    def test_default_message_intel_special_characters(self) -> None:
        special_text = '<script>alert("xss")</script>'
        intel = DefaultMessageIntel(text=special_text)
        result = intel.render_to_str()

        assert result == special_text

    def test_default_message_intel_unicode(self) -> None:
        unicode_text = 'Hello 世界 🌍'
        intel = DefaultMessageIntel(text=unicode_text)
        result = intel.render_to_str()

        assert result == unicode_text

    def test_render_template_to_str_with_none_context(self) -> None:
        intel = DefaultMessageIntel(text='Test')
        result = intel.render_template_to_str(context_data=None)

        assert isinstance(result, str)

    def test_render_template_to_str_with_empty_context(self) -> None:
        intel = DefaultMessageIntel(text='Test')
        result = intel.render_template_to_str(context_data={})

        assert isinstance(result, str)

    def test_custom_message_intel_override_extra_data(self) -> None:
        intel = CustomMessageIntel(text='Test', extra_data='Override')

        assert intel.extra_data == 'Override'
        assert intel.render_to_str() == 'Test - Override'

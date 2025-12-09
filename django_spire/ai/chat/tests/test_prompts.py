from __future__ import annotations

from django_spire.ai.chat.intelligence.prompts import chat_system_prompt
from django_spire.ai.context.models import Organization
from django_spire.core.tests.test_cases import BaseTestCase


class ChatPromptsTests(BaseTestCase):
    def test_chat_system_prompt_returns_prompt(self) -> None:
        prompt = chat_system_prompt()

        assert prompt is not None

    def test_chat_system_prompt_contains_assistant_text(self) -> None:
        prompt = chat_system_prompt()
        prompt_str = prompt.to_str()

        assert 'chat assistant' in prompt_str.lower()

    def test_chat_system_prompt_contains_rules(self) -> None:
        prompt = chat_system_prompt()
        prompt_str = prompt.to_str()

        assert 'rules' in prompt_str.lower()

    def test_chat_system_prompt_with_organization(self) -> None:
        Organization.objects.create(
            name='Test Company',
            description='A test company for testing purposes'
        )

        prompt = chat_system_prompt()
        prompt_str = prompt.to_str()

        assert 'organization' in prompt_str.lower()

    def test_chat_system_prompt_without_organization(self) -> None:
        prompt = chat_system_prompt()
        prompt_str = prompt.to_str()

        assert prompt_str is not None
        assert len(prompt_str) > 0

    def test_chat_system_prompt_ai_illusion_rule(self) -> None:
        prompt = chat_system_prompt()
        prompt_str = prompt.to_str()

        assert 'ai' in prompt_str.lower() or 'illusion' in prompt_str.lower()

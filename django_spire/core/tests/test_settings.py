from __future__ import annotations

from django.test import TestCase

from django_spire import settings


class TestDefaultSettings(TestCase):
    def test_ai_chat_routers_contains_spire(self) -> None:
        assert 'SPIRE' in settings.DJANGO_SPIRE_AI_CHAT_ROUTERS

    def test_ai_default_chat_router(self) -> None:
        assert settings.DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER == 'SPIRE'

    def test_ai_intent_chat_routers_contains_knowledge_search(self) -> None:
        assert 'KNOWLEDGE_SEARCH' in settings.DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS

    def test_ai_intent_chat_routers_structure(self) -> None:
        knowledge_search = settings.DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS['KNOWLEDGE_SEARCH']

        assert 'INTENT_DESCRIPTION' in knowledge_search
        assert 'REQUIRED_PERMISSION' in knowledge_search
        assert 'CHAT_ROUTER' in knowledge_search

    def test_ai_persona_name(self) -> None:
        assert settings.DJANGO_SPIRE_AI_PERSONA_NAME == 'AI Assistant'

    def test_default_theme_mode(self) -> None:
        assert settings.DJANGO_SPIRE_DEFAULT_THEME_MODE == 'light'

    def test_search_registry_default_empty(self) -> None:
        assert settings.DJANGO_SPIRE_SEARCH_REGISTRY == {}

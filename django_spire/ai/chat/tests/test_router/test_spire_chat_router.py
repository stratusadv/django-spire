from __future__ import annotations

from unittest.mock import Mock, patch

from django.test import RequestFactory, override_settings

from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.ai.chat.router import SpireChatRouter
from django_spire.core.tests.test_cases import BaseTestCase


class TestSpireChatRouter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.super_user

    def test_router_can_be_instantiated(self) -> None:
        router = SpireChatRouter()
        assert isinstance(router, SpireChatRouter)

    def test_default_chat_callable_returns_message_intel(self) -> None:
        router = SpireChatRouter()

        with patch('django_spire.ai.chat.router.Bot') as MockBot:
            mock_bot_instance = Mock()
            MockBot.return_value = mock_bot_instance
            mock_bot_instance.llm.prompt_to_intel.return_value = DefaultMessageIntel(text='Response')

            result = router._default_chat_callable(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            assert isinstance(result, DefaultMessageIntel)
            mock_bot_instance.llm.prompt_to_intel.assert_called_once()

    @override_settings(DJANGO_SPIRE_AI_PERSONA_NAME='Test Bot')
    def test_default_callable_uses_persona_name(self) -> None:
        router = SpireChatRouter()

        with patch('django_spire.ai.chat.router.Bot') as MockBot:
            mock_bot_instance = Mock()
            MockBot.return_value = mock_bot_instance
            mock_bot_instance.llm.prompt_to_intel.return_value = DefaultMessageIntel(text='Response')

            router._default_chat_callable(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            assert MockBot.called

    def test_workflow_uses_intent_decoder(self) -> None:
        router = SpireChatRouter()

        with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
            mock_decoder_instance = Mock()
            mock_decoder.return_value = mock_decoder_instance
            mock_decoder_instance.process.return_value = [lambda **kwargs: DefaultMessageIntel(text='Response')]

            result = router.workflow(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            mock_decoder.assert_called_once()
            assert isinstance(result, DefaultMessageIntel)

    @override_settings(DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={})
    def test_workflow_with_no_intent_routers(self) -> None:
        router = SpireChatRouter()

        with patch.object(router, '_default_chat_callable') as mock_default:
            mock_default.return_value = DefaultMessageIntel(text='Default response')

            with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
                mock_decoder_instance = Mock()
                mock_decoder.return_value = mock_decoder_instance
                mock_decoder_instance.process.return_value = [mock_default]

                result = router.workflow(
                    request=self.request,
                    user_input='Hello',
                    message_history=None
                )

                assert isinstance(result, DefaultMessageIntel)

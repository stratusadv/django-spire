from __future__ import annotations

from unittest.mock import Mock, patch

from dandy.llm.request.message import MessageHistory
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

    def test_workflow_passes_message_history_to_decoder(self) -> None:
        router = SpireChatRouter()
        message_history = MessageHistory()

        with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
            mock_decoder_instance = Mock()
            mock_decoder.return_value = mock_decoder_instance
            mock_decoder_instance.process.return_value = [
                lambda **kwargs: DefaultMessageIntel(text='Response')
            ]

            router.workflow(
                request=self.request,
                user_input='Hello',
                message_history=message_history
            )

            mock_decoder.assert_called_once()

    def test_workflow_returns_message_intel(self) -> None:
        router = SpireChatRouter()

        with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
            mock_decoder_instance = Mock()
            mock_decoder.return_value = mock_decoder_instance
            mock_decoder_instance.process.return_value = [
                lambda **kwargs: DefaultMessageIntel(text='Test Response')
            ]

            result = router.workflow(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            assert isinstance(result, DefaultMessageIntel)
            assert result.text == 'Test Response'

    @override_settings(DJANGO_SPIRE_AI_PERSONA_NAME='Custom Persona')
    def test_default_callable_with_custom_persona(self) -> None:
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

            assert mock_bot_instance.llm_role is not None

    def test_default_callable_passes_message_history(self) -> None:
        router = SpireChatRouter()
        message_history = MessageHistory()

        with patch('django_spire.ai.chat.router.Bot') as MockBot:
            mock_bot_instance = Mock()
            MockBot.return_value = mock_bot_instance
            mock_bot_instance.llm.prompt_to_intel.return_value = DefaultMessageIntel(text='Response')

            router._default_chat_callable(
                request=self.request,
                user_input='Hello',
                message_history=message_history
            )

            call_kwargs = mock_bot_instance.llm.prompt_to_intel.call_args[1]
            assert call_kwargs['message_history'] == message_history

    def test_default_callable_passes_user_input(self) -> None:
        router = SpireChatRouter()

        with patch('django_spire.ai.chat.router.Bot') as MockBot:
            mock_bot_instance = Mock()
            MockBot.return_value = mock_bot_instance
            mock_bot_instance.llm.prompt_to_intel.return_value = DefaultMessageIntel(text='Response')

            router._default_chat_callable(
                request=self.request,
                user_input='Test input',
                message_history=None
            )

            call_kwargs = mock_bot_instance.llm.prompt_to_intel.call_args[1]
            assert call_kwargs['prompt'] == 'Test input'

    def test_default_callable_uses_default_message_intel(self) -> None:
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

            call_kwargs = mock_bot_instance.llm.prompt_to_intel.call_args[1]
            assert call_kwargs['intel_class'] == DefaultMessageIntel

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

    def test_default_chat_callable_returns_default_without_permission(self) -> None:
        router = SpireChatRouter()

        self.request.user = Mock()
        self.request.user.has_perm.return_value = False

        result = router._default_chat_callable(
            request=self.request,
            user_input='Hello',
            message_history=None
        )

        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'Sorry, I could not find any information on that.'

    def test_default_chat_callable_calls_knowledge_workflow_with_permission(self) -> None:
        router = SpireChatRouter()

        with patch('django_spire.knowledge.intelligence.workflows.knowledge_workflow.knowledge_search_workflow') as mock_workflow:
            mock_workflow.return_value = DefaultMessageIntel(text='Knowledge response')

            result = router._default_chat_callable(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            mock_workflow.assert_called_once_with(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            assert isinstance(result, DefaultMessageIntel)

    # def test_workflow_uses_intent_decoder(self) -> None:
        # Todo(brayden) here is another place the decoder tests need to be updated.
    #     router = SpireChatRouter()
    #
    #     with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
    #         mock_decoder_instance = Mock()
    #         mock_decoder.return_value = mock_decoder_instance
    #         mock_decoder_instance.process.return_value = [lambda **kwargs: DefaultMessageIntel(text='Response')]
    #
    #         result = router.workflow(
    #             request=self.request,
    #             user_input='Hello',
    #             message_history=None
    #         )
    #
    #         mock_decoder.assert_called_once()
    #         assert isinstance(result, DefaultMessageIntel)

    # @override_settings(DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={})
    # def test_workflow_with_no_intent_routers(self) -> None:
    #     router = SpireChatRouter()
    #
    #     with patch.object(router, '_default_chat_callable') as mock_default:
    #         mock_default.return_value = DefaultMessageIntel(text='Default response')
    #
    #         with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
    #             mock_decoder_instance = Mock()
    #             mock_decoder.return_value = mock_decoder_instance
    #             mock_decoder_instance.process.return_value = [mock_default]
    #
    #             result = router.workflow(
    #                 request=self.request,
    #                 user_input='Hello',
    #                 message_history=None
    #             )
    #
    #             assert isinstance(result, DefaultMessageIntel)

    # def test_workflow_passes_message_history_to_decoder(self) -> None:
    #     router = SpireChatRouter()
    #     message_history = MessageHistory()
    #
    #     with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
    #         mock_decoder_instance = Mock()
    #         mock_decoder.return_value = mock_decoder_instance
    #         mock_decoder_instance.process.return_value = [
    #             lambda **kwargs: DefaultMessageIntel(text='Response')
    #         ]
    #
    #         router.workflow(
    #             request=self.request,
    #             user_input='Hello',
    #             message_history=message_history
    #         )
    #
    #         mock_decoder.assert_called_once()

    # def test_workflow_returns_message_intel(self) -> None:
    #     router = SpireChatRouter()
    #
    #     with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
    #         mock_decoder_instance = Mock()
    #         mock_decoder.return_value = mock_decoder_instance
    #         mock_decoder_instance.process.return_value = [
    #             lambda **kwargs: DefaultMessageIntel(text='Test Response')
    #         ]
    #
    #         result = router.workflow(
    #             request=self.request,
    #             user_input='Hello',
    #             message_history=None
    #         )
    #
    #         assert isinstance(result, DefaultMessageIntel)
    #         assert result.text == 'Test Response'

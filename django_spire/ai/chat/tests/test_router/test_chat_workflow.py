from __future__ import annotations

from unittest.mock import Mock, patch

from django.test import RequestFactory, override_settings

from django_spire.ai.chat.intelligence.workflows.chat_workflow import chat_workflow
from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.ai.chat.router import BaseChatRouter
from django_spire.core.tests.test_cases import BaseTestCase


class MockRouter(BaseChatRouter):
    def workflow(self, request, user_input, message_history=None) -> DefaultMessageIntel:
        return DefaultMessageIntel(text='Mock response')


class TestChatWorkflow(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.super_user

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='SPIRE',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'SPIRE': 'django_spire.ai.chat.router.SpireChatRouter'
        }
    )
    def test_workflow_loads_default_router(self) -> None:
        with patch('django_spire.ai.chat.intelligence.workflows.chat_workflow.get_callable_from_module_string_and_validate_arguments') as mock_get_callable:
            mock_router_class = Mock()
            mock_router_instance = Mock()
            mock_router_instance.process.return_value = DefaultMessageIntel(text='Response')
            mock_router_class.return_value = mock_router_instance
            mock_get_callable.return_value = mock_router_class

            result = chat_workflow(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            mock_get_callable.assert_called_once_with(
                'django_spire.ai.chat.router.SpireChatRouter',
                []
            )

            assert isinstance(result, DefaultMessageIntel)

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='CUSTOM',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'CUSTOM': 'django_spire.ai.chat.tests.test_router.test_chat_workflow.MockRouter'
        }
    )
    def test_workflow_loads_custom_router(self) -> None:
        result = chat_workflow(
            request=self.request,
            user_input='Hello',
            message_history=None
        )

        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'Mock response'

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='NONEXISTENT',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'SPIRE': 'django_spire.ai.chat.router.SpireChatRouter'
        }
    )
    def test_workflow_falls_back_when_router_not_found(self) -> None:
        with patch('django_spire.ai.chat.intelligence.workflows.chat_workflow.get_callable_from_module_string_and_validate_arguments') as mock_get_callable:
            mock_router_class = Mock()
            mock_router_instance = Mock()
            mock_router_instance.process.return_value = DefaultMessageIntel(text='Fallback')
            mock_router_class.return_value = mock_router_instance
            mock_get_callable.return_value = mock_router_class

            result = chat_workflow(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

            assert isinstance(result, DefaultMessageIntel)

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='TEST',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'TEST': 'django_spire.ai.chat.tests.test_router.test_chat_workflow.MockRouter'
        }
    )
    def test_workflow_passes_message_history(self) -> None:
        from dandy.llm.request.message import MessageHistory

        message_history = MessageHistory()

        with patch('django_spire.ai.chat.tests.test_router.test_chat_workflow.MockRouter.process') as mock_process:
            mock_process.return_value = DefaultMessageIntel(text='Response')

            chat_workflow(
                request=self.request,
                user_input='Hello',
                message_history=message_history
            )

            mock_process.assert_called_once()
            call_kwargs = mock_process.call_args[1]
            assert call_kwargs['message_history'] == message_history

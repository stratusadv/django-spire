from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from dandy.llm.request.message import MessageHistory
from django.contrib.auth.models import Permission, User
from django.test import RequestFactory, override_settings

from django_spire.ai.chat.intelligence.decoders.intent_decoder import generate_intent_decoder
from django_spire.ai.chat.intelligence.workflows.chat_workflow import chat_workflow
from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.chat.router import BaseChatRouter
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class KnowledgeRouter(BaseChatRouter):
    def workflow(
        self,
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> DefaultMessageIntel:
        return DefaultMessageIntel(text='Knowledge search result')


class SupportRouter(BaseChatRouter):
    def workflow(
        self,
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> DefaultMessageIntel:
        return DefaultMessageIntel(text='Support response')


class TestRouterIntegration(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.super_user

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='SPIRE',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'SPIRE': 'django_spire.ai.chat.router.SpireChatRouter',
            'KNOWLEDGE': 'django_spire.ai.chat.tests.test_router.test_integration.KnowledgeRouter',
            'SUPPORT': 'django_spire.ai.chat.tests.test_router.test_integration.SupportRouter',
        },
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={
            'KNOWLEDGE_SEARCH': {
                'INTENT_DESCRIPTION': 'User asking about documentation',
                'REQUIRED_PERMISSION': 'auth.view_user',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_integration.KnowledgeRouter',
            },
            'SUPPORT': {
                'INTENT_DESCRIPTION': 'User needs support',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_integration.SupportRouter',
            }
        }
    )
    def test_intent_routing_with_permission(self) -> None:
        permission = Permission.objects.get(codename='view_user')
        self.super_user.user_permissions.add(permission)

        with patch('django_spire.ai.chat.router.generate_intent_decoder') as mock_decoder:
            mock_decoder_instance = type('MockDecoder', (), {
                'process': lambda self, user_input, **kwargs: [
                    lambda **kwargs: KnowledgeRouter().workflow(**kwargs)
                ]
            })()

            mock_decoder.return_value = mock_decoder_instance

            result = chat_workflow(
                request=self.request,
                user_input='Tell me about the documentation',
                message_history=None
            )

            assert isinstance(result, BaseMessageIntel)

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='SUPPORT',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'SUPPORT': 'django_spire.ai.chat.tests.test_router.test_integration.SupportRouter',
        }
    )
    def test_direct_router_selection(self) -> None:
        result = chat_workflow(
            request=self.request,
            user_input='I need help',
            message_history=None
        )

        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'Support response'

    @override_settings(
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={
            'RESTRICTED': {
                'INTENT_DESCRIPTION': 'Restricted intent',
                'REQUIRED_PERMISSION': 'auth.delete_user',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_integration.SupportRouter',
            }
        }
    )
    def test_intent_excluded_without_permission(self) -> None:
        regular_user = User.objects.create_user(username='regular', password='test')

        request = self.factory.get('/')
        request.user = regular_user

        decoder = generate_intent_decoder(request=request, default_callable=None)

        assert 'Restricted intent' not in decoder.mapping

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='KNOWLEDGE',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'KNOWLEDGE': 'django_spire.ai.chat.tests.test_router.test_integration.KnowledgeRouter',
        }
    )
    def test_end_to_end_workflow(self) -> None:
        message_history = MessageHistory()
        message_history.add_message(role='user', content='Previous message')

        result = chat_workflow(
            request=self.request,
            user_input='Current message',
            message_history=message_history
        )

        assert isinstance(result, BaseMessageIntel)
        assert isinstance(result, DefaultMessageIntel)

    @override_settings(
        DJANGO_SPIRE_AI_CHAT_ROUTERS={}
    )
    def test_workflow_handles_empty_routers(self) -> None:
        with patch('django_spire.ai.chat.intelligence.workflows.chat_workflow.get_callable_from_module_string_and_validate_arguments') as mock_get_callable:
            mock_router_class = Mock()
            mock_router_instance = Mock()
            mock_router_instance.process.return_value = DefaultMessageIntel(text='Fallback')
            mock_router_class.return_value = mock_router_instance
            mock_get_callable.return_value = mock_router_class

            result = chat_workflow(
                request=self.request,
                user_input='Test',
                message_history=None
            )

            assert isinstance(result, DefaultMessageIntel)

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='KNOWLEDGE',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'KNOWLEDGE': 'django_spire.ai.chat.tests.test_router.test_integration.KnowledgeRouter',
            'SUPPORT': 'django_spire.ai.chat.tests.test_router.test_integration.SupportRouter',
        }
    )
    def test_router_selection_by_key(self) -> None:
        result = chat_workflow(
            request=self.request,
            user_input='Test',
            message_history=None
        )

        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'Knowledge search result'

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='SUPPORT',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'SUPPORT': 'django_spire.ai.chat.tests.test_router.test_integration.SupportRouter',
        }
    )
    def test_workflow_with_none_message_history(self) -> None:
        result = chat_workflow(
            request=self.request,
            user_input='Test input',
            message_history=None
        )

        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'Support response'

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='SUPPORT',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'SUPPORT': 'django_spire.ai.chat.tests.test_router.test_integration.SupportRouter',
        }
    )
    def test_workflow_preserves_user_input(self) -> None:
        test_input = 'This is a specific test input'

        with patch.object(SupportRouter, 'workflow', wraps=SupportRouter().workflow) as mock_workflow:
            mock_workflow.return_value = DefaultMessageIntel(text='Response')

            chat_workflow(
                request=self.request,
                user_input=test_input,
                message_history=None
            )

    @override_settings(
        DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER='KNOWLEDGE',
        DJANGO_SPIRE_AI_CHAT_ROUTERS={
            'KNOWLEDGE': 'django_spire.ai.chat.tests.test_router.test_integration.KnowledgeRouter',
        },
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={}
    )
    def test_workflow_without_intent_routers(self) -> None:
        result = chat_workflow(
            request=self.request,
            user_input='Test',
            message_history=None
        )

        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'Knowledge search result'

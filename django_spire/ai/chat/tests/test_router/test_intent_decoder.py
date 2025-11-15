from __future__ import annotations

from unittest.mock import Mock

from django.contrib.auth.models import Permission, User
from django.test import RequestFactory, override_settings

from django_spire.ai.chat.intelligence.decoders.intent_decoder import generate_intent_decoder
from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.ai.chat.router import BaseChatRouter
from django_spire.core.tests.test_cases import BaseTestCase


class TestRouter(BaseChatRouter):
    def workflow(self, request, user_input, message_history=None) -> DefaultMessageIntel:
        return DefaultMessageIntel(text='Test response')


class TestIntentDecoder(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.super_user

    @override_settings(DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={})
    def test_decoder_with_no_intents(self) -> None:
        decoder = generate_intent_decoder(
            request=self.request,
            default_callable=lambda **kwargs: DefaultMessageIntel(text='Default')
        )

        assert decoder is not None
        assert len(decoder.mapping) == 1

    @override_settings(
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={
            'TEST_INTENT': {
                'INTENT_DESCRIPTION': 'Test intent description',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_intent_decoder.TestRouter',
            }
        }
    )
    def test_decoder_adds_intent_without_permission(self) -> None:
        decoder = generate_intent_decoder(
            request=self.request,
            default_callable=None
        )

        assert len(decoder.mapping) == 1
        assert 'Test intent description' in decoder.mapping

    @override_settings(
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={
            'TEST_INTENT': {
                'INTENT_DESCRIPTION': 'Test intent with permission',
                'REQUIRED_PERMISSION': 'auth.add_user',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_intent_decoder.TestRouter',
            }
        }
    )
    def test_decoder_checks_required_permission(self) -> None:
        permission = Permission.objects.get(codename='add_user')
        self.super_user.user_permissions.add(permission)

        decoder = generate_intent_decoder(
            request=self.request,
            default_callable=None
        )

        assert 'Test intent with permission' in decoder.mapping

    @override_settings(
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={
            'TEST_INTENT': {
                'INTENT_DESCRIPTION': 'Test intent with permission',
                'REQUIRED_PERMISSION': 'auth.add_user',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_intent_decoder.TestRouter',
            }
        }
    )
    def test_decoder_excludes_intent_without_permission(self) -> None:
        regular_user = User.objects.create_user(username='regular', password='test')

        request = self.factory.get('/')
        request.user = regular_user

        decoder = generate_intent_decoder(
            request=request,
            default_callable=None
        )

        assert 'Test intent with permission' not in decoder.mapping

    @override_settings(
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={
            'INVALID_ROUTER': {
                'INTENT_DESCRIPTION': 'Invalid router',
                'CHAT_ROUTER': 'non.existent.router.InvalidRouter',
            }
        }
    )
    def test_decoder_handles_import_error(self) -> None:
        decoder = generate_intent_decoder(
            request=self.request,
            default_callable=None
        )

        assert 'Invalid router' not in decoder.mapping

    def test_decoder_adds_default_callable(self) -> None:
        default_callable = Mock()

        decoder = generate_intent_decoder(
            request=self.request,
            default_callable=default_callable
        )

        assert "None of the above choices match the user's intent" in decoder.mapping

    @override_settings(
        DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS={
            'INTENT_1': {
                'INTENT_DESCRIPTION': 'First intent',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_intent_decoder.TestRouter',
            },
            'INTENT_2': {
                'INTENT_DESCRIPTION': 'Second intent',
                'CHAT_ROUTER': 'django_spire.ai.chat.tests.test_router.test_intent_decoder.TestRouter',
            }
        }
    )
    def test_decoder_adds_multiple_intents(self) -> None:
        decoder = generate_intent_decoder(
            request=self.request,
            default_callable=None
        )

        assert 'First intent' in decoder.mapping
        assert 'Second intent' in decoder.mapping
        assert len(decoder.mapping) == 2

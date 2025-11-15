from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.test import RequestFactory

from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.chat.router import BaseChatRouter
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


class TestBaseChatRouter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.super_user

    def test_workflow_is_abstract_method(self) -> None:
        with pytest.raises(TypeError):
            BaseChatRouter()

    def test_process_calls_workflow(self) -> None:
        class TestRouter(BaseChatRouter):
            workflow_called = False

            def workflow(
                self,
                request: WSGIRequest,
                user_input: str,
                message_history: MessageHistory | None = None
            ) -> BaseMessageIntel:
                self.workflow_called = True
                return DefaultMessageIntel(text='Test response')

        router = TestRouter()
        result = router.process(
            request=self.request,
            user_input='Hello',
            message_history=None
        )

        assert router.workflow_called
        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'Test response'

    def test_process_validates_workflow_return_type(self) -> None:
        class InvalidRouter(BaseChatRouter):
            def workflow(self, request, user_input, message_history=None) -> str:
                return 'Invalid return type'

        router = InvalidRouter()

        with pytest.raises(TypeError) as cm:
            router.process(
                request=self.request,
                user_input='Hello',
                message_history=None
            )

        assert 'BaseMessageIntel' in str(cm.value)

    def test_process_handles_none_return(self) -> None:
        class NoneRouter(BaseChatRouter):
            def workflow(self, request, user_input, message_history=None) -> None:
                return None

        router = NoneRouter()
        result = router.process(
            request=self.request,
            user_input='Hello',
            message_history=None
        )

        assert isinstance(result, DefaultMessageIntel)
        assert result.text == 'I apologize, but I was unable to process your request.'

    def test_process_accepts_all_parameters(self) -> None:
        from dandy.llm.request.message import MessageHistory

        class ParamTestRouter(BaseChatRouter):
            received_params = {}

            def workflow(self, request, user_input, message_history=None) -> DefaultMessageIntel:
                self.received_params = {
                    'request': request,
                    'user_input': user_input,
                    'message_history': message_history
                }
                return DefaultMessageIntel(text='Success')

        router = ParamTestRouter()
        message_history = MessageHistory()

        router.process(
            request=self.request,
            user_input='Test input',
            message_history=message_history
        )

        assert router.received_params['request'] == self.request
        assert router.received_params['user_input'] == 'Test input'
        assert router.received_params['message_history'] == message_history

from __future__ import annotations

from django_spire.ai.chat.choices import MessageResponseType
from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.ai.chat.responses import MessageResponse, MessageResponseGroup
from django_spire.core.tests.test_cases import BaseTestCase


class MessageResponseTests(BaseTestCase):
    def test_message_response_creation(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        )

        assert response.type == MessageResponseType.REQUEST
        assert response.sender == 'User'
        assert response.message_intel.text == 'Hello'

    def test_message_response_with_timestamp(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello'),
            message_timestamp='Jan 01, 2024 at 12:00 PM'
        )

        assert response.message_timestamp == 'Jan 01, 2024 at 12:00 PM'

    def test_message_response_with_synthesis_speech(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.RESPONSE,
            sender='Assistant',
            message_intel=DefaultMessageIntel(text='Hello'),
            synthesis_speech=True
        )

        assert response.synthesis_speech is True

    def test_message_response_render_to_html_string_request(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        )

        html = response.render_to_html_string()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_message_response_render_to_html_string_response(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.RESPONSE,
            sender='Assistant',
            message_intel=DefaultMessageIntel(text='Hello')
        )

        html = response.render_to_html_string()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_message_response_render_to_html_string_loading(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.LOADING_RESPONSE,
            sender='Assistant',
            message_intel=DefaultMessageIntel(text='Loading...')
        )

        html = response.render_to_html_string()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_message_response_render_with_context_data(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        )

        html = response.render_to_html_string(context_data={'chat_id': 123})

        assert isinstance(html, str)

    def test_message_response_default_synthesis_speech(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        )

        assert response.synthesis_speech is False

    def test_message_response_default_timestamp(self) -> None:
        response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        )

        assert response.message_timestamp is None


class MessageResponseGroupTests(BaseTestCase):
    def test_message_response_group_creation(self) -> None:
        group = MessageResponseGroup()

        assert len(group.message_responses) == 0

    def test_add_message_response(self) -> None:
        group = MessageResponseGroup()
        response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        )

        group.add_message_response(response)

        assert len(group.message_responses) == 1

    def test_add_multiple_message_responses(self) -> None:
        group = MessageResponseGroup()

        for i in range(5):
            response = MessageResponse(
                type=MessageResponseType.REQUEST,
                sender='User',
                message_intel=DefaultMessageIntel(text=f'Message {i}')
            )
            group.add_message_response(response)

        assert len(group.message_responses) == 5

    def test_render_to_html_string_empty(self) -> None:
        group = MessageResponseGroup()

        html = group.render_to_html_string()

        assert html == ''

    def test_render_to_html_string_with_messages(self) -> None:
        group = MessageResponseGroup()
        group.add_message_response(MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        ))
        group.add_message_response(MessageResponse(
            type=MessageResponseType.RESPONSE,
            sender='Assistant',
            message_intel=DefaultMessageIntel(text='Hi')
        ))

        html = group.render_to_html_string()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_render_to_html_string_with_context(self) -> None:
        group = MessageResponseGroup()
        group.add_message_response(MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        ))

        html = group.render_to_html_string(context_data={'chat_id': 123})

        assert isinstance(html, str)

    def test_render_to_html_string_with_is_loading(self) -> None:
        group = MessageResponseGroup()
        group.add_message_response(MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        ))

        html = group.render_to_html_string(context_data={'is_loading': True})

        assert isinstance(html, str)

    def test_render_to_html_string_default_is_loading(self) -> None:
        group = MessageResponseGroup()
        group.add_message_response(MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        ))

        html = group.render_to_html_string(context_data={})

        assert isinstance(html, str)


class MessageResponseTypeTests(BaseTestCase):
    def test_request_type(self) -> None:
        assert MessageResponseType.REQUEST.value == 'request'

    def test_response_type(self) -> None:
        assert MessageResponseType.RESPONSE.value == 'response'

    def test_loading_response_type(self) -> None:
        assert MessageResponseType.LOADING_RESPONSE.value == 'loading_response'

from __future__ import annotations

from django_spire.ai.chat.choices import MessageResponseType
from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.responses import MessageResponse
from django_spire.core.tests.test_cases import BaseTestCase


class ChatModelTests(BaseTestCase):
    def test_chat_creation(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Test Chat'
        )

        assert chat.name == 'Test Chat'
        assert chat.user == self.super_user

    def test_chat_str_short_name(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Short Name'
        )

        assert str(chat) == 'Short Name'

    def test_chat_str_long_name(self) -> None:
        long_name = 'A' * 100
        chat = Chat.objects.create(
            user=self.super_user,
            name=long_name
        )

        assert len(str(chat)) == 51
        assert str(chat).endswith('...')

    def test_chat_name_shortened_short(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Short'
        )

        assert chat.name_shortened == 'Short'

    def test_chat_name_shortened_long(self) -> None:
        long_name = 'A' * 50
        chat = Chat.objects.create(
            user=self.super_user,
            name=long_name
        )

        assert len(chat.name_shortened) == 27
        assert chat.name_shortened.endswith('...')

    def test_chat_is_empty(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Empty Chat'
        )

        assert chat.is_empty

    def test_chat_is_not_empty(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Chat with messages'
        )

        message_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        )
        chat.add_message_response(message_response)

        assert not chat.is_empty

    def test_add_message_response(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Test Chat'
        )

        message_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Test message')
        )
        chat.add_message_response(message_response)

        assert chat.messages.count() == 1

    def test_add_message_response_updates_last_message_datetime(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Test Chat'
        )

        initial_datetime = chat.last_message_datetime

        message_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Test')
        )
        chat.add_message_response(message_response)
        chat.refresh_from_db()

        assert chat.last_message_datetime >= initial_datetime

    def test_generate_message_history(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Test Chat'
        )

        chat.add_message_response(MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Hello')
        ))
        chat.add_message_response(MessageResponse(
            type=MessageResponseType.RESPONSE,
            sender='Assistant',
            message_intel=DefaultMessageIntel(text='Hi there')
        ))

        message_history = chat.generate_message_history()

        assert message_history is not None

    def test_generate_message_history_exclude_last(self) -> None:
        chat = Chat.objects.create(
            user=self.super_user,
            name='Test Chat'
        )

        chat.add_message_response(MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Message 1')
        ))
        chat.add_message_response(MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Message 2')
        ))

        message_history = chat.generate_message_history(exclude_last_message=True)

        assert message_history is not None


class ChatMessageModelTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.chat = Chat.objects.create(
            user=self.super_user,
            name='Test Chat'
        )

    def test_chat_message_str_short(self) -> None:
        message_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Short')
        )
        self.chat.add_message_response(message_response)

        message = self.chat.messages.first()

        assert str(message) == 'Short'

    def test_chat_message_str_long(self) -> None:
        long_text = 'A' * 100
        message_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text=long_text)
        )
        self.chat.add_message_response(message_response)

        message = self.chat.messages.first()

        assert len(str(message)) == 67
        assert str(message).endswith('...')

    def test_chat_message_intel_property(self) -> None:
        message_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Test intel')
        )
        self.chat.add_message_response(message_response)

        message = self.chat.messages.first()

        assert isinstance(message.intel, DefaultMessageIntel)
        assert message.intel.text == 'Test intel'

    def test_chat_message_role_request(self) -> None:
        message_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Test')
        )
        self.chat.add_message_response(message_response)

        message = self.chat.messages.first()

        assert message.role == 'user'

    def test_chat_message_role_response(self) -> None:
        message_response = MessageResponse(
            type=MessageResponseType.RESPONSE,
            sender='Assistant',
            message_intel=DefaultMessageIntel(text='Test')
        )
        self.chat.add_message_response(message_response)

        message = self.chat.messages.first()

        assert message.role == 'assistant'

    def test_chat_message_to_message_response(self) -> None:
        original_response = MessageResponse(
            type=MessageResponseType.REQUEST,
            sender='User',
            message_intel=DefaultMessageIntel(text='Test')
        )
        self.chat.add_message_response(original_response)

        message = self.chat.messages.first()
        converted_response = message.to_message_response()

        assert isinstance(converted_response, MessageResponse)
        assert converted_response.type == MessageResponseType.REQUEST
        assert converted_response.sender == 'User'


class ChatQuerySetTests(BaseTestCase):
    def test_by_user(self) -> None:
        Chat.objects.create(user=self.super_user, name='User Chat')

        result = Chat.objects.by_user(self.super_user)

        assert result.count() == 1

    def test_search(self) -> None:
        Chat.objects.create(user=self.super_user, name='Python Programming')
        Chat.objects.create(user=self.super_user, name='Django Framework')

        result = Chat.objects.search('Python')

        assert result.count() == 1
        assert result.first().name == 'Python Programming'

    def test_search_case_insensitive(self) -> None:
        Chat.objects.create(user=self.super_user, name='Python Programming')

        result = Chat.objects.search('python')

        assert result.count() == 1


class ChatMessageQuerySetTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.chat = Chat.objects.create(
            user=self.super_user,
            name='Test Chat'
        )

    def test_newest_by_count(self) -> None:
        for i in range(25):
            message_response = MessageResponse(
                type=MessageResponseType.REQUEST,
                sender='User',
                message_intel=DefaultMessageIntel(text=f'Message {i}')
            )
            self.chat.add_message_response(message_response)

        messages = self.chat.messages.newest_by_count(20)

        assert len(messages) == 20

    def test_newest_by_count_reversed(self) -> None:
        for i in range(5):
            message_response = MessageResponse(
                type=MessageResponseType.REQUEST,
                sender='User',
                message_intel=DefaultMessageIntel(text=f'Message {i}')
            )
            self.chat.add_message_response(message_response)

        messages = self.chat.messages.newest_by_count_reversed(5)

        assert len(messages) == 5

from __future__ import annotations

from django.test import TestCase

from django_spire.ai.sms.models import SmsConversation, SmsMessage


class SmsConversationModelTests(TestCase):
    def test_conversation_creation(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        assert conversation.phone_number == '+15551234567'
        assert conversation.messages.count() == 0
        assert conversation.is_empty

    def test_conversation_str(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        assert '+15551234567' in str(conversation)
        assert 'SMS Conversation' in str(conversation)

    def test_add_message(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        message = conversation.add_message(body='Hello', is_inbound=True, twilio_sid='')

        assert message.body == 'Hello'
        assert message.is_inbound

        message = conversation.add_message(body='Hi there', is_inbound=False, twilio_sid='')

        assert message.body == 'Hi there'
        assert not message.is_inbound

        assert conversation.messages.count() == 2
        assert not conversation.is_empty

    def test_add_message_updates_last_message_datetime(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        initial_datetime = conversation.last_message_datetime

        conversation.add_message(body='Test', is_inbound=True, twilio_sid='')
        conversation.refresh_from_db()

        assert conversation.last_message_datetime >= initial_datetime

    def test_generate_message_history(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        conversation.add_message(body='User message 1', is_inbound=True, twilio_sid='')
        conversation.add_message(body='Assistant response 1', is_inbound=False, twilio_sid='')
        conversation.add_message(body='User message 2', is_inbound=True, twilio_sid='')

        message_history = conversation.generate_message_history(
            message_count=20,
            exclude_last_message=True
        )

        assert message_history is not None

    def test_generate_message_history_includes_last_message(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        conversation.add_message(body='User message 1', is_inbound=True, twilio_sid='')
        conversation.add_message(body='User message 2', is_inbound=True, twilio_sid='')

        message_history = conversation.generate_message_history(
            message_count=20,
            exclude_last_message=False
        )

        assert message_history is not None

    def test_is_empty_property(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        assert conversation.is_empty

        conversation.add_message(body='Test', is_inbound=True, twilio_sid='')

        assert not conversation.is_empty


class SmsMessageModelTests(TestCase):
    def test_message_creation(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test message',
            is_inbound=True,
            twilio_sid='SM123'
        )

        assert message.body == 'Test message'
        assert message.is_inbound
        assert message.twilio_sid == 'SM123'

    def test_message_str_short(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        message = SmsMessage.objects.create(
            conversation=conversation,
            body='Short message',
            is_inbound=True
        )

        assert 'Inbound' in str(message)
        assert 'Short message' in str(message)

    def test_message_str_long(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        long_body = 'A' * 100
        message = SmsMessage.objects.create(
            conversation=conversation,
            body=long_body,
            is_inbound=True
        )

        assert '...' in str(message)

    def test_direction_property_inbound(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test',
            is_inbound=True
        )

        assert message.direction == 'Inbound'

    def test_direction_property_outbound(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test',
            is_inbound=False
        )

        assert message.direction == 'Outbound'

    def test_is_outbound_property(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        inbound_message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test',
            is_inbound=True
        )

        outbound_message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test',
            is_inbound=False
        )

        assert not inbound_message.is_outbound
        assert outbound_message.is_outbound

    def test_role_property_inbound(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test',
            is_inbound=True
        )

        assert message.role == 'user'

    def test_role_property_outbound(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test',
            is_inbound=False
        )

        assert message.role == 'assistant'

    def test_message_is_processed_default(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        message = SmsMessage.objects.create(
            conversation=conversation,
            body='Test',
            is_inbound=True
        )

        assert message.is_processed is False


class SmsQuerySetTests(TestCase):
    def test_by_phone_number(self) -> None:
        SmsConversation.objects.create(phone_number='+15551234567')
        SmsConversation.objects.create(phone_number='+15559876543')

        result = SmsConversation.objects.by_phone_number('+15551234567')

        assert result.count() == 1
        assert result.first().phone_number == '+15551234567'

    def test_newest_by_count(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        for i in range(25):
            conversation.add_message(body=f'Message {i}', is_inbound=True, twilio_sid='')

        messages = conversation.messages.newest_by_count(20)

        assert len(messages) == 20

    def test_newest_by_count_reversed(self) -> None:
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        for i in range(5):
            conversation.add_message(body=f'Message {i}', is_inbound=True, twilio_sid='')

        messages = conversation.messages.newest_by_count_reversed(5)

        assert len(messages) == 5

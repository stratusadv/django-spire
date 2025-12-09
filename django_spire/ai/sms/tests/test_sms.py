from django.test import TestCase

from django_spire.ai.sms.models import SmsConversation


class SmsModelTests(TestCase):
    def test_conversation_creation(self):
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        assert conversation.phone_number == '+15551234567'
        assert conversation.messages.count() == 0
        assert conversation.is_empty

    def test_add_message(self):
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )

        message = conversation.add_message(body="Hello", is_inbound=True, twilio_sid='')
        assert message.body == "Hello"
        assert message.is_inbound

        message = conversation.add_message(body="Hi there", is_inbound=False, twilio_sid='')
        assert message.body == "Hi there"
        assert not message.is_inbound

        assert conversation.messages.count() == 2
        assert not conversation.is_empty


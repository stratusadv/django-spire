from django.test import TestCase

from django_spire.ai.sms.models import SmsConversation


class SmsModelTests(TestCase):
    def test_conversation_creation(self):
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        self.assertEqual(conversation.phone_number, '+15551234567')
        self.assertEqual(conversation.messages.count(), 0)
        self.assertTrue(conversation.is_empty)

    def test_add_message(self):
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        
        message = conversation.add_message(body="Hello", is_inbound=True, twilio_sid='')
        self.assertEqual(message.body, "Hello")
        self.assertTrue(message.is_inbound)

        message = conversation.add_message(body="Hi there", is_inbound=False, twilio_sid='')
        self.assertEqual(message.body, "Hi there")
        self.assertFalse(message.is_inbound)

        self.assertEqual(conversation.messages.count(), 2)
        self.assertFalse(conversation.is_empty)


from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock

from django_spire.ai.sms.models import SmsConversation, SmsMessage
from django_spire.ai.sms.tools import send_sms


class SmsModelTests(TestCase):
    def test_conversation_creation(self):
        """Test that an SMS conversation can be created"""
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        self.assertEqual(conversation.phone_number, '+15551234567')
        self.assertEqual(conversation.messages.count(), 0)
        self.assertTrue(conversation.is_empty)

    def test_add_message(self):
        """Test that messages can be added to a conversation"""
        conversation = SmsConversation.objects.create(
            phone_number='+15551234567'
        )
        
        # Add an inbound message
        message = conversation.add_message(body="Hello", is_inbound=True)
        self.assertEqual(message.body, "Hello")
        self.assertTrue(message.is_inbound)
        self.assertFalse(message.is_viewed)
        self.assertTrue(conversation.has_unread_messages)
        
        # Add an outbound message
        message = conversation.add_message(body="Hi there", is_inbound=False)
        self.assertEqual(message.body, "Hi there")
        self.assertFalse(message.is_inbound)
        self.assertTrue(message.is_viewed)
        
        # Check conversation state
        self.assertEqual(conversation.messages.count(), 2)
        self.assertFalse(conversation.is_empty)


class SmsWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('ai:sms:webhook')
    
    @patch('twilio.twiml.messaging_response.MessagingResponse')
    def test_webhook_receives_message(self, mock_messaging_response):
        """Test that the webhook receives and processes messages"""
        # Mock the TwiML response
        mock_response = MagicMock()
        mock_messaging_response.return_value = mock_response
        mock_response.message.return_value = mock_response
        mock_response.__str__.return_value = '<Response><Message>You said: Hello</Message></Response>'
        
        # Send a POST request to the webhook
        response = self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Hello',
                'MessageSid': 'SM123456789'
            }
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Check that a conversation was created
        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        self.assertEqual(conversation.messages.count(), 2)  # Inbound and outbound
        
        # Check the messages
        inbound_message = conversation.messages.filter(is_inbound=True).first()
        self.assertEqual(inbound_message.body, 'Hello')
        self.assertEqual(inbound_message.twilio_sid, 'SM123456789')
        
        outbound_message = conversation.messages.filter(is_inbound=False).first()
        self.assertEqual(outbound_message.body, 'You said: Hello')


class SmsSendTests(TestCase):
    @patch('twilio.rest.Client')
    def test_send_sms(self, mock_client):
        """Test that SMS messages can be sent"""
        # Mock the Twilio client
        mock_messages = MagicMock()
        mock_client.return_value.messages = mock_messages
        mock_message = MagicMock()
        mock_message.sid = 'SM123456789'
        mock_messages.create.return_value = mock_message
        
        # Send an SMS
        with patch('django.conf.settings') as mock_settings:
            mock_settings.TWILIO_ACCOUNT_SID = 'test_sid'
            mock_settings.TWILIO_AUTH_TOKEN = 'test_token'
            mock_settings.TWILIO_PHONE_NUMBER = '+15551234567'
            
            message = send_sms('+15559876543', 'Test message')
        
        # Check that the message was created
        self.assertEqual(message.body, 'Test message')
        self.assertEqual(message.twilio_sid, 'SM123456789')
        self.assertFalse(message.is_inbound)
        
        # Check that the conversation was created
        conversation = SmsConversation.objects.get(phone_number='+15559876543')
        self.assertEqual(conversation.messages.count(), 1)
from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.email.helper import EmailHelper, SendGridEmailHelper
from django_spire.notification.email.tests.factories import create_test_email_notification


class EmailHelperTests(BaseTestCase):
    def test_normalize_recipients_handles_lists_strings_and_empty_values(self):
        assert EmailHelper._normalize_recipients(['a@example.com', 'b@example.com']) == [
            'a@example.com',
            'b@example.com',
        ]
        assert EmailHelper._normalize_recipients('a@example.com') == ['a@example.com']
        assert EmailHelper._normalize_recipients('') == []
        assert EmailHelper._normalize_recipients(None) == []
        assert EmailHelper._normalize_recipients({}) == []

    @override_settings(DEFAULT_FROM_EMAIL='noreply@example.com', SENDGRID_TEMPLATE_ID='d-default-template')
    def test_sendgrid_helper_single_recipient_template_data(self):
        email_notification = create_test_email_notification(
            to=['single@example.com'], cc=['cc@example.com'], bcc=['bcc@example.com'], context_data={'extra': 'value'}
        )

        helper = SendGridEmailHelper(email_notification.notification)

        assert helper.to == ['single@example.com']
        assert helper.cc == ['cc@example.com']
        assert helper.bcc == ['bcc@example.com']
        assert helper.template_id == 'd-default-template'
        assert helper.template_data['to'] == 'single@example.com'
        assert helper.template_data['from'] == 'noreply@example.com'
        assert helper.template_data['extra'] == 'value'

    @override_settings(DEFAULT_FROM_EMAIL='noreply@example.com', SENDGRID_TEMPLATE_ID='d-default-template')
    @patch('django_spire.notification.email.helper.EmailMessage')
    def test_sendgrid_helper_multiple_recipients_send(self, mock_email_message_class: MagicMock):
        mock_message = MagicMock()
        mock_email_message_class.return_value = mock_message

        email_notification = create_test_email_notification(
            to=['first@example.com', 'second@example.com'],
            cc=['cc1@example.com', 'cc2@example.com'],
            bcc=['bcc1@example.com'],
            template_id='d-custom-template',
        )

        helper = SendGridEmailHelper(email_notification.notification, fail_silently=True)
        helper.send()

        mock_email_message_class.assert_called_once_with(
            from_email='noreply@example.com',
            to=['first@example.com', 'second@example.com'],
            cc=['cc1@example.com', 'cc2@example.com'],
            bcc=['bcc1@example.com'],
            attachments=[],
        )
        assert mock_message.template_id == 'd-custom-template'
        assert mock_message.dynamic_template_data['to'] == 'first@example.com, second@example.com'
        mock_message.send.assert_called_once_with(fail_silently=True)

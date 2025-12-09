from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.email.tests.factories import create_test_email_notification
from django_spire.notification.models import Notification


class EmailNotificationModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.email_notification = create_test_email_notification()

    def test_str(self):
        expected = f'{self.email_notification.notification.title} - {self.email_notification.to_email_address}'
        assert str(self.email_notification) == expected

    def test_notification_relationship(self):
        assert self.email_notification.notification is not None
        assert isinstance(self.email_notification.notification, Notification)

    def test_default_template_id(self):
        assert self.email_notification.template_id == ''

    def test_default_context_data(self):
        assert self.email_notification.context_data == {}

    def test_default_cc(self):
        assert self.email_notification.cc == []

    def test_default_bcc(self):
        assert self.email_notification.bcc == []

    def test_to_email_address(self):
        assert self.email_notification.to_email_address == 'test@example.com'

    def test_with_cc(self):
        email_notification = create_test_email_notification(
            cc=['cc1@example.com', 'cc2@example.com']
        )
        assert email_notification.cc == ['cc1@example.com', 'cc2@example.com']

    def test_with_bcc(self):
        email_notification = create_test_email_notification(
            bcc=['bcc1@example.com', 'bcc2@example.com']
        )
        assert email_notification.bcc == ['bcc1@example.com', 'bcc2@example.com']

    def test_with_context_data(self):
        email_notification = create_test_email_notification(
            context_data={'key': 'value'}
        )
        assert email_notification.context_data == {'key': 'value'}

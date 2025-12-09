from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import (
    NotificationPriorityChoices,
    NotificationStatusChoices,
    NotificationTypeChoices,
)


class NotificationTypeChoicesTests(BaseTestCase):
    def test_app_value(self):
        assert NotificationTypeChoices.APP == 'app'

    def test_email_value(self):
        assert NotificationTypeChoices.EMAIL == 'email'

    def test_push_value(self):
        assert NotificationTypeChoices.PUSH == 'push'

    def test_sms_value(self):
        assert NotificationTypeChoices.SMS == 'sms'

    def test_choices_count(self):
        assert len(NotificationTypeChoices.choices) == 4


class NotificationStatusChoicesTests(BaseTestCase):
    def test_pending_value(self):
        assert NotificationStatusChoices.PENDING == 'pending'

    def test_processing_value(self):
        assert NotificationStatusChoices.PROCESSING == 'processing'

    def test_sent_value(self):
        assert NotificationStatusChoices.SENT == 'sent'

    def test_errored_value(self):
        assert NotificationStatusChoices.ERRORED == 'errored'

    def test_failed_value(self):
        assert NotificationStatusChoices.FAILED == 'failed'

    def test_choices_count(self):
        assert len(NotificationStatusChoices.choices) == 5


class NotificationPriorityChoicesTests(BaseTestCase):
    def test_low_value(self):
        assert NotificationPriorityChoices.LOW == 'low'

    def test_medium_value(self):
        assert NotificationPriorityChoices.MEDIUM == 'medium'

    def test_high_value(self):
        assert NotificationPriorityChoices.HIGH == 'high'

    def test_choices_count(self):
        assert len(NotificationPriorityChoices.choices) == 3

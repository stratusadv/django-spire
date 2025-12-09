from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import (
    NotificationPriorityChoices,
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.tests.factories import create_test_notification


class NotificationModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.notification = create_test_notification()

    def test_default_status_is_pending(self):
        assert self.notification.status == NotificationStatusChoices.PENDING

    def test_default_priority_is_low(self):
        assert self.notification.priority == NotificationPriorityChoices.LOW

    def test_get_type_display(self):
        self.notification.type = NotificationTypeChoices.APP
        assert self.notification.get_type_display() == 'App'

        self.notification.type = NotificationTypeChoices.EMAIL
        assert self.notification.get_type_display() == 'Email'

        self.notification.type = NotificationTypeChoices.SMS
        assert self.notification.get_type_display() == 'Sms'

        self.notification.type = NotificationTypeChoices.PUSH
        assert self.notification.get_type_display() == 'Push'

    def test_get_status_display(self):
        self.notification.status = NotificationStatusChoices.PENDING
        assert self.notification.get_status_display() == 'Pending'

        self.notification.status = NotificationStatusChoices.PROCESSING
        assert self.notification.get_status_display() == 'Processing'

        self.notification.status = NotificationStatusChoices.SENT
        assert self.notification.get_status_display() == 'Sent'

        self.notification.status = NotificationStatusChoices.ERRORED
        assert self.notification.get_status_display() == 'Errored'

        self.notification.status = NotificationStatusChoices.FAILED
        assert self.notification.get_status_display() == 'Failed'

    def test_get_priority_display(self):
        self.notification.priority = NotificationPriorityChoices.LOW
        assert self.notification.get_priority_display() == 'Low'

        self.notification.priority = NotificationPriorityChoices.MEDIUM
        assert self.notification.get_priority_display() == 'Medium'

        self.notification.priority = NotificationPriorityChoices.HIGH
        assert self.notification.get_priority_display() == 'High'

    def test_user_relationship(self):
        assert self.notification.user is not None
        assert self.notification.user.pk is not None

    def test_created_datetime_auto_set(self):
        assert self.notification.created_datetime is not None

    def test_sent_datetime_null_by_default(self):
        assert self.notification.sent_datetime is None

    def test_content_object_null_by_default(self):
        assert self.notification.content_object is None
        assert self.notification.content_type is None
        assert self.notification.object_id is None

from __future__ import annotations

import pytest

from django.core.exceptions import ValidationError

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import NotificationStatusChoices, NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.email.tests.factories import create_test_email_notification
from django_spire.notification.models import Notification


class EmailNotificationQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_email_queryset_user')
        self.email_notification = create_test_email_notification(
            user=self.user, status=NotificationStatusChoices.SENT, to=['primary@example.com', 'secondary@example.com']
        )

    def test_by_to_email(self):
        other_notification = create_test_email_notification(user=self.user, to=['someone@example.com'])

        result = EmailNotification.objects.by_to_email('secondary@example.com')
        assert self.email_notification in result
        assert other_notification not in result

    def test_by_user(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_email_notification(user=other_user)

        result = EmailNotification.objects.by_user(self.user)
        assert self.email_notification in result
        assert other_notification not in result

    def test_by_users(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_email_notification(user=other_user)

        result = EmailNotification.objects.by_users([self.user, other_user])
        assert self.email_notification in result
        assert other_notification in result

    def test_is_sent(self):
        pending_notification = create_test_email_notification(user=self.user, status=NotificationStatusChoices.PENDING)

        result = EmailNotification.objects.is_sent()
        assert self.email_notification in result
        assert pending_notification not in result

    def test_bulk_create_validates_recipients(self):
        valid_notification = Notification.objects.create(
            user=self.user, type=NotificationTypeChoices.EMAIL, title='Valid Bulk', body='Body'
        )
        invalid_notification = Notification.objects.create(
            user=self.user, type=NotificationTypeChoices.EMAIL, title='Invalid Bulk', body='Body'
        )
        initial_count = EmailNotification.objects.count()

        with pytest.raises(ValidationError):
            EmailNotification.objects.bulk_create(
                [
                    EmailNotification(notification=valid_notification, to=['valid@example.com']),
                    EmailNotification(notification=invalid_notification, to=['invalid-email']),
                ]
            )

        assert EmailNotification.objects.count() == initial_count

    def test_bulk_update_validates_recipient_fields(self):
        self.email_notification.cc = ['primary@example.com']

        with pytest.raises(ValidationError) as exc_info:
            EmailNotification.objects.bulk_update([self.email_notification], ['cc'])

        assert 'cc' in exc_info.value.message_dict

    def test_bulk_update_non_recipient_fields(self):
        self.email_notification.template_id = 'd-bulk-123'
        EmailNotification.objects.bulk_update([self.email_notification], ['template_id'])
        self.email_notification.refresh_from_db()
        assert self.email_notification.template_id == 'd-bulk-123'

    def test_update_validates_recipients(self):
        with pytest.raises(ValidationError) as exc_info:
            EmailNotification.objects.filter(pk=self.email_notification.pk).update(to=['bad-email'])

        assert 'to' in exc_info.value.message_dict

    def test_bulk_create_syncs_deprecated_to_email_address(self):
        notification = Notification.objects.create(
            user=self.user, type=NotificationTypeChoices.EMAIL, title='Legacy Bulk', body='Body'
        )

        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'):
            created = EmailNotification.objects.bulk_create(
                [EmailNotification(notification=notification, to_email_address='legacy-bulk@example.com')]
            )

        created[0].refresh_from_db()
        assert created[0].to == ['legacy-bulk@example.com']
        assert created[0].to_email_address == 'legacy-bulk@example.com'

    def test_bulk_update_keeps_to_and_to_email_address_in_sync(self):
        self.email_notification.to = ['synced@example.com', 'extra@example.com']
        EmailNotification.objects.bulk_update([self.email_notification], ['to'])
        self.email_notification.refresh_from_db()
        assert self.email_notification.to == ['synced@example.com', 'extra@example.com']
        assert self.email_notification.to_email_address == 'synced@example.com'

        self.email_notification.to_email_address = 'bulk-legacy@example.com'
        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'):
            EmailNotification.objects.bulk_update([self.email_notification], ['to_email_address'])

        self.email_notification.refresh_from_db()
        assert self.email_notification.to == ['bulk-legacy@example.com']
        assert self.email_notification.to_email_address == 'bulk-legacy@example.com'

    def test_update_with_deprecated_to_email_address_warns_and_syncs_to(self):
        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'):
            EmailNotification.objects.filter(pk=self.email_notification.pk).update(
                to_email_address='qs-legacy@example.com'
            )

        self.email_notification.refresh_from_db()
        assert self.email_notification.to == ['qs-legacy@example.com']
        assert self.email_notification.to_email_address == 'qs-legacy@example.com'

    def test_legacy_filter_by_to_email_address_matches_first_recipient(self):
        result = EmailNotification.objects.filter(to_email_address='primary@example.com')
        assert self.email_notification in result

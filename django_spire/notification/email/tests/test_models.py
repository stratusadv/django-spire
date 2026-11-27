from __future__ import annotations

import pytest

from django.core.exceptions import ValidationError

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.email.tests.factories import create_test_email_notification
from django_spire.notification.models import Notification


class EmailNotificationModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.email_notification = create_test_email_notification()

    def test_str_single_recipient(self):
        expected = f'{self.email_notification.notification.title} - test@example.com'
        assert str(self.email_notification) == expected

    def test_str_multiple_recipients(self):
        email_notification = create_test_email_notification(to=['first@example.com', 'second@example.com'])
        expected = f'{email_notification.notification.title} - first@example.com, second@example.com'
        assert str(email_notification) == expected

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

    def test_to_default_single_recipient(self):
        assert self.email_notification.to == ['test@example.com']

    def test_to_multiple_recipients(self):
        email_notification = create_test_email_notification(to=['first@example.com', 'second@example.com'])
        assert email_notification.to == ['first@example.com', 'second@example.com']

    def test_with_cc(self):
        email_notification = create_test_email_notification(cc=['cc1@example.com', 'cc2@example.com'])
        assert email_notification.cc == ['cc1@example.com', 'cc2@example.com']

    def test_with_bcc(self):
        email_notification = create_test_email_notification(bcc=['bcc1@example.com', 'bcc2@example.com'])
        assert email_notification.bcc == ['bcc1@example.com', 'bcc2@example.com']

    def test_with_context_data(self):
        email_notification = create_test_email_notification(context_data={'key': 'value'})
        assert email_notification.context_data == {'key': 'value'}

    def test_full_clean_passes_with_defaults(self):
        self.email_notification.full_clean()

    def test_create_rejects_empty_to(self):
        with pytest.raises(ValidationError) as exc_info:
            create_test_email_notification(to=[])

        assert 'to' in exc_info.value.message_dict

    def test_create_rejects_string_to(self):
        with pytest.raises(ValidationError) as exc_info:
            create_test_email_notification(to='test@example.com')

        assert 'to' in exc_info.value.message_dict

    def test_create_rejects_invalid_emails_in_to_cc_bcc(self):
        with pytest.raises(ValidationError) as exc_info:
            create_test_email_notification(to=['not-an-email'], cc=['also-bad'], bcc=['still-bad'])

        assert set(exc_info.value.message_dict.keys()) == {'to', 'cc', 'bcc'}

    def test_create_rejects_duplicates_within_field(self):
        with pytest.raises(ValidationError) as exc_info:
            create_test_email_notification(to=['dup@example.com', 'DUP@example.com'])

        assert 'to' in exc_info.value.message_dict

    def test_create_rejects_duplicate_between_to_and_cc(self):
        with pytest.raises(ValidationError) as exc_info:
            create_test_email_notification(to=['user@example.com'], cc=['USER@example.com'])

        assert 'cc' in exc_info.value.message_dict

    def test_create_rejects_duplicate_between_to_and_bcc(self):
        with pytest.raises(ValidationError) as exc_info:
            create_test_email_notification(to=['user@example.com'], bcc=['user@example.com'])

        assert 'bcc' in exc_info.value.message_dict

    def test_create_rejects_duplicate_between_cc_and_bcc(self):
        with pytest.raises(ValidationError) as exc_info:
            create_test_email_notification(to=['to@example.com'], cc=['shared@example.com'], bcc=['SHARED@example.com'])

        assert 'bcc' in exc_info.value.message_dict

    def test_full_clean_rejects_cross_field_duplicate(self):
        self.email_notification.cc = ['TEST@example.com']

        with pytest.raises(ValidationError) as exc_info:
            self.email_notification.full_clean()

        assert 'cc' in exc_info.value.message_dict

    def test_save_update_fields_validates_when_recipient_field_updated(self):
        self.email_notification.cc = ['bad-email']

        with pytest.raises(ValidationError) as exc_info:
            self.email_notification.save(update_fields=['cc'])

        assert 'cc' in exc_info.value.message_dict

    def test_save_update_fields_skips_validation_for_non_recipient_fields(self):
        self.email_notification.template_id = 'd-template-123'
        self.email_notification.save(update_fields=['template_id'])
        self.email_notification.refresh_from_db()
        assert self.email_notification.template_id == 'd-template-123'

    def test_to_mirrors_first_recipient_to_deprecated_to_email_address(self):
        email_notification = create_test_email_notification(to=['first@example.com', 'second@example.com'])
        email_notification.refresh_from_db()
        assert email_notification.to_email_address == 'first@example.com'

    def test_create_with_deprecated_to_email_address_warns_and_populates_to(self):
        notification = Notification.objects.create(
            user=self.super_user, type=NotificationTypeChoices.EMAIL, title='Legacy', body='Body'
        )

        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'):
            email_notification = EmailNotification.objects.create(
                notification=notification,
                to_email_address='legacy@example.com',
            )

        email_notification.refresh_from_db()
        assert email_notification.to == ['legacy@example.com']
        assert email_notification.to_email_address == 'legacy@example.com'

    def test_create_with_invalid_deprecated_to_email_address_raises_validation_error(self):
        notification = Notification.objects.create(
            user=self.super_user, type=NotificationTypeChoices.EMAIL, title='Bad Legacy', body='Body'
        )

        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'), pytest.raises(ValidationError):
            EmailNotification.objects.create(notification=notification, to_email_address='not-an-email')

    def test_full_clean_with_deprecated_to_email_address_syncs_to(self):
        notification = Notification.objects.create(
            user=self.super_user, type=NotificationTypeChoices.EMAIL, title='Clean Legacy', body='Body'
        )
        email_notification = EmailNotification(notification=notification, to_email_address='clean@example.com')

        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'):
            email_notification.full_clean()

        assert email_notification.to == ['clean@example.com']

    def test_updating_deprecated_to_email_address_updates_to(self):
        self.email_notification.to_email_address = 'updated@example.com'

        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'):
            self.email_notification.save(update_fields=['to_email_address'])

        self.email_notification.refresh_from_db()
        assert self.email_notification.to == ['updated@example.com']
        assert self.email_notification.to_email_address == 'updated@example.com'

    def test_updating_to_with_update_fields_also_syncs_to_email_address(self):
        self.email_notification.to = ['new@example.com', 'second@example.com']
        self.email_notification.save(update_fields=['to'])
        self.email_notification.refresh_from_db()
        assert self.email_notification.to == ['new@example.com', 'second@example.com']
        assert self.email_notification.to_email_address == 'new@example.com'

    def test_refresh_from_db_updates_recipient_snapshots(self):
        EmailNotification.objects.filter(pk=self.email_notification.pk).update(to=['refreshed@example.com'])
        self.email_notification.refresh_from_db()
        assert self.email_notification.to == ['refreshed@example.com']

        self.email_notification.to_email_address = 'after-refresh@example.com'
        with pytest.warns(DeprecationWarning, match='to_email_address is deprecated'):
            self.email_notification.save()

        self.email_notification.refresh_from_db()
        assert self.email_notification.to == ['after-refresh@example.com']
        assert self.email_notification.to_email_address == 'after-refresh@example.com'

    def test_save_update_fields_with_deferred_to_email_address_syncs_new_to(self):
        deferred_notification = EmailNotification.objects.only('id', 'to').get(pk=self.email_notification.pk)
        deferred_notification.to = ['deferred-new@example.com', 'second@example.com']
        deferred_notification.save(update_fields=['to'])

        reloaded = EmailNotification.objects.get(pk=self.email_notification.pk)
        assert reloaded.to == ['deferred-new@example.com', 'second@example.com']
        assert reloaded.to_email_address == 'deferred-new@example.com'

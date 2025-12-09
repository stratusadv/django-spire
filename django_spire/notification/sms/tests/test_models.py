from __future__ import annotations

import uuid

from django.utils.timezone import now, timedelta

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.models import Notification
from django_spire.notification.sms.choices import SmsMediaContentTypeChoices
from django_spire.notification.sms.models import SmsTemporaryMedia
from django_spire.notification.sms.tests.factories import create_test_sms_notification


class SmsNotificationModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.sms_notification = create_test_sms_notification()

    def test_str(self):
        expected = f'{self.sms_notification.to_phone_number} - {self.sms_notification.notification.title}'
        assert str(self.sms_notification) == expected

    def test_notification_relationship(self):
        assert self.sms_notification.notification is not None
        assert isinstance(self.sms_notification.notification, Notification)

    def test_to_phone_number(self):
        assert self.sms_notification.to_phone_number == '5551234567'

    def test_media_url_default_none(self):
        assert self.sms_notification.media_url is None

    def test_temporary_media_default_none(self):
        assert self.sms_notification.temporary_media is None

    def test_with_media_url(self):
        sms_notification = create_test_sms_notification(
            media_url='https://example.com/image.png'
        )
        assert sms_notification.media_url == 'https://example.com/image.png'


class SmsTemporaryMediaModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.temporary_media = SmsTemporaryMedia.objects.create(
            content='base64encodedcontent',
            content_type=SmsMediaContentTypeChoices.PNG,
            name='test_image.png',
            expire_datetime=now() + timedelta(hours=1),
            external_access_key=uuid.uuid4(),
        )

    def test_str(self):
        expected = f'{self.temporary_media.name} - {self.temporary_media.content_type}'
        assert str(self.temporary_media) == expected

    def test_is_expired_false(self):
        assert self.temporary_media.is_expired() is False

    def test_is_expired_true(self):
        self.temporary_media.expire_datetime = now() - timedelta(hours=1)
        self.temporary_media.save()
        assert self.temporary_media.is_expired() is True

    def test_external_url(self):
        url = self.temporary_media.external_url
        assert str(self.temporary_media.external_access_key) in url

    def test_content_type_png(self):
        assert self.temporary_media.content_type == SmsMediaContentTypeChoices.PNG

    def test_content_type_jpeg(self):
        media = SmsTemporaryMedia.objects.create(
            content='base64encodedcontent',
            content_type=SmsMediaContentTypeChoices.JPEG,
            name='test_image.jpg',
            expire_datetime=now() + timedelta(hours=1),
            external_access_key=uuid.uuid4(),
        )
        assert media.content_type == SmsMediaContentTypeChoices.JPEG

from __future__ import annotations

import uuid

from django.utils.timezone import now, timedelta

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.sms.choices import SmsMediaContentTypeChoices
from django_spire.notification.sms.models import SmsTemporaryMedia


class SmsTemporaryMediaTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.expired_media = SmsTemporaryMedia.objects.create(
            content='base64content',
            content_type=SmsMediaContentTypeChoices.PNG,
            name='expired.png',
            expire_datetime=now() - timedelta(hours=1),
            external_access_key=uuid.uuid4(),
        )
        self.valid_media = SmsTemporaryMedia.objects.create(
            content='base64content',
            content_type=SmsMediaContentTypeChoices.PNG,
            name='valid.png',
            expire_datetime=now() + timedelta(hours=1),
            external_access_key=uuid.uuid4(),
        )

    def test_is_expired_true(self):
        assert self.expired_media.is_expired() is True

    def test_is_expired_false(self):
        assert self.valid_media.is_expired() is False

    def test_external_url_contains_access_key(self):
        url = self.valid_media.external_url
        assert str(self.valid_media.external_access_key) in url

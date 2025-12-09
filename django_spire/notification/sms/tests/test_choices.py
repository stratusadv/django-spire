from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.sms.choices import SmsMediaContentTypeChoices


class SmsMediaContentTypeChoicesTests(BaseTestCase):
    def test_png_value(self):
        assert SmsMediaContentTypeChoices.PNG == 'image/png'

    def test_jpeg_value(self):
        assert SmsMediaContentTypeChoices.JPEG == 'image/jpeg'

    def test_choices_count(self):
        assert len(SmsMediaContentTypeChoices.choices) == 2

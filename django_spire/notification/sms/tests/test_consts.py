from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.sms.consts import (
    TWILIO_SMS_BATCH_SIZE_NAME,
    TWILIO_UNSUCCESSFUL_STATUSES,
)


class SmsConstsTests(BaseTestCase):
    def test_twilio_unsuccessful_statuses(self):
        assert 'failed' in TWILIO_UNSUCCESSFUL_STATUSES
        assert 'undelivered' in TWILIO_UNSUCCESSFUL_STATUSES
        assert len(TWILIO_UNSUCCESSFUL_STATUSES) == 2

    def test_twilio_sms_batch_size_name(self):
        assert TWILIO_SMS_BATCH_SIZE_NAME == 'TWILIO_SMS_BATCH_SIZE'

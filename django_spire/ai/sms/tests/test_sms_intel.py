from __future__ import annotations

from django_spire.ai.sms.intel import SmsIntel
from django_spire.core.tests.test_cases import BaseTestCase


class SmsIntelTests(BaseTestCase):
    def test_sms_intel_creation(self) -> None:
        intel = SmsIntel(body='Test message')

        assert intel.body == 'Test message'

    def test_sms_intel_empty_body(self) -> None:
        intel = SmsIntel(body='')

        assert intel.body == ''

    def test_sms_intel_long_body(self) -> None:
        long_body = 'A' * 1000
        intel = SmsIntel(body=long_body)

        assert intel.body == long_body
        assert len(intel.body) == 1000

    def test_sms_intel_unicode_body(self) -> None:
        unicode_body = 'Hello 世界 🌍'
        intel = SmsIntel(body=unicode_body)

        assert intel.body == unicode_body

    def test_sms_intel_model_dump(self) -> None:
        intel = SmsIntel(body='Test')
        dump = intel.model_dump()

        assert 'body' in dump
        assert dump['body'] == 'Test'

    def test_sms_intel_special_characters(self) -> None:
        special_body = 'Line 1\nLine 2\tTabbed'
        intel = SmsIntel(body=special_body)

        assert intel.body == special_body

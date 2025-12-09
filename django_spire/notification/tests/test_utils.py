from __future__ import annotations

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.utils import get_throttle_sleep_time


class NotificationUtilsTests(BaseTestCase):
    @override_settings(NOTIFICATION_THROTTLE_RATE_PER_MINUTE=60)
    def test_get_throttle_sleep_time_60_per_minute(self):
        result = get_throttle_sleep_time()
        assert result == 1.0

    @override_settings(NOTIFICATION_THROTTLE_RATE_PER_MINUTE=120)
    def test_get_throttle_sleep_time_120_per_minute(self):
        result = get_throttle_sleep_time()
        assert result == 2.0

    @override_settings(NOTIFICATION_THROTTLE_RATE_PER_MINUTE=30)
    def test_get_throttle_sleep_time_30_per_minute(self):
        result = get_throttle_sleep_time()
        assert result == 0.5

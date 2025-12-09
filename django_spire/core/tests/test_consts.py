from __future__ import annotations

from django.test import TestCase

from django_spire.consts import (
    __VERSION__,
    MAINTENANCE_MODE_SETTINGS_NAME,
    NOTIFICATION_THROTTLE_RATE_PER_MINUTE_SETTINGS_NAME,
)


class TestConsts(TestCase):
    def test_maintenance_mode_settings_name(self) -> None:
        assert MAINTENANCE_MODE_SETTINGS_NAME == 'MAINTENANCE_MODE'

    def test_notification_throttle_rate_settings_name(self) -> None:
        assert NOTIFICATION_THROTTLE_RATE_PER_MINUTE_SETTINGS_NAME == 'NOTIFICATION_THROTTLE_RATE_PER_MINUTE'

    def test_version_is_string(self) -> None:
        assert isinstance(__VERSION__, str)

    def test_version_format(self) -> None:
        parts = __VERSION__.split('.')

        assert len(parts) == 3

        for part in parts:
            assert part.isdigit()

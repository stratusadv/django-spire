from __future__ import annotations

from django.conf import settings

from django_spire.consts import NOTIFICATION_THROTTLE_RATE_PER_MINUTE_SETTINGS_NAME


def get_throttle_sleep_time() -> float:
    return float(getattr(settings, NOTIFICATION_THROTTLE_RATE_PER_MINUTE_SETTINGS_NAME) / 60)

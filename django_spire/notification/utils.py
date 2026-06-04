from __future__ import annotations

from django_spire.conf import settings


def get_throttle_sleep_time() -> float:
    return float(settings.DJANGO_SPIRE_NOTIFICATION_THROTTLE_RATE_PER_MINUTE / 60)

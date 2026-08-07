from __future__ import annotations

from django.core.cache import cache
from django.utils.timezone import now

from django_spire.conf import settings


DAY_SECONDS = 86400
MINUTE_SECONDS = 60


def throttle_allowed(phone_number: str) -> bool:
    current_datetime = now()

    minute_window = current_datetime.strftime('%Y%m%d%H%M')
    day_window = current_datetime.strftime('%Y%m%d')

    minute_key = f'django_spire_ai_sms_throttle_minute_{phone_number}_{minute_window}'
    day_key = f'django_spire_ai_sms_throttle_day_{phone_number}_{day_window}'

    minute_count = _counter_increment(minute_key, MINUTE_SECONDS)
    day_count = _counter_increment(day_key, DAY_SECONDS)

    minute_rate_max = settings.DJANGO_SPIRE_AI_SMS_THROTTLE_RATE_PER_MINUTE
    day_rate_max = settings.DJANGO_SPIRE_AI_SMS_THROTTLE_RATE_PER_DAY

    if minute_count > minute_rate_max:
        return False

    if day_count > day_rate_max:
        return False

    return True


def _counter_increment(key: str, timeout_seconds: int) -> int:
    cache.add(key, 0, timeout_seconds)

    return cache.incr(key)

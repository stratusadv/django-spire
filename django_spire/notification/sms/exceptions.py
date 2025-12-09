from __future__ import annotations

from django_spire.exceptions import DjangoSpireError


class SmsNotificationError(DjangoSpireError):
    pass


class SmsTemporaryMediaError(SmsNotificationError):
    pass


class TwilioError(Exception):
    pass


class TwilioAPIConcurrentError(TwilioError):
    pass

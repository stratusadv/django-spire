from __future__ import annotations

from django_spire.exceptions import DjangoSpireError


class SmsNotificationError(DjangoSpireError):
    pass


class SmsTemporaryMediaError(SmsNotificationError):
    pass


class TwilioError(Exception):
    pass


class InvalidPhoneNumberError(TwilioError):
    def __init__(self, phone_number: str) -> None:
        super().__init__(f'Invalid phone number format: {phone_number}')


class TwilioResponseError(TwilioError):
    def __init__(self, error_code: int | None, error_message: str | None) -> None:
        super().__init__(
            f'Twilio Error: code={error_code}, message={error_message}'
        )


class TwilioAPIConcurrentError(TwilioError):
    pass

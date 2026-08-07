from __future__ import annotations

from twilio.rest import Client

from django_spire.conf import settings


def phone_number_normalize(phone_number: str) -> str | None:
    digits = ''.join(filter(str.isdigit, phone_number))

    if len(digits) == 10:
        return '+1' + digits

    if len(digits) == 11 and digits.startswith('1'):
        return '+' + digits

    return None


def message_send(phone_number: str, body: str) -> None:
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone_number = settings.TWILIO_PHONE_NUMBER

    if not account_sid or not auth_token or not from_phone_number:
        message = 'twilio credentials are not configured'
        raise RuntimeError(message)

    client = Client(account_sid, auth_token)

    client.messages.create(
        to=phone_number,
        from_=from_phone_number,
        body=body,
    )

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from django_spire.notification.choices import NotificationStatusChoices

if TYPE_CHECKING:
    from django_spire.notification.sms.models import SmsTemporaryMedia


def update_unsent_notification_status_for_deleted_temporary_media(
    temporary_media_to_delete: list[SmsTemporaryMedia]
):
    for temporary_media in temporary_media_to_delete:
        if temporary_media.has_unsent_notifications():
            temporary_media.sms_notifications.all().update(
                notification__status=NotificationStatusChoices.ERRORED,
                notification__status_message='SMS temporary media expired before notification was sent',
            )

def format_to_international_phone_number(phone_number: str, country_code: str='1') -> str:
    """
    Args: phone_number:
    Returns: international phone number format
    """

    if not phone_number:
        message = f'No phone number provided: {phone_number}'
        raise ValueError(message)

    # Remove extension numbers
    main_number = re.split(r'(?:ext\.?|x)\s*\d+', phone_number, flags=re.IGNORECASE)[0]

    # Get all digit characters
    digit_number = re.sub(r'\D', '', main_number)
    if digit_number.startswith(country_code) and len(digit_number) == 10 + len(country_code):
        digit_number = digit_number[len(country_code):]

    # Check if the number is in local format or already in international format
    if len(digit_number) == 10:
        return f'+{country_code}{digit_number}'

    if len(digit_number) == 10 + len(country_code) and digit_number.startswith(country_code):
        return f'+{digit_number}'

    message = f'Invalid phone number: {phone_number}'
    raise ValueError(message)

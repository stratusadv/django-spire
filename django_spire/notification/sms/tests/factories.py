from __future__ import annotations

from django.contrib.auth.models import User

from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.models import Notification
from django_spire.notification.sms.models import SmsNotification


def create_test_sms_notification(**kwargs) -> SmsNotification:
    if 'notification' not in kwargs:
        user = kwargs.pop('user', None) or User.objects.first()
        notification = Notification.objects.create(
            user=user,
            type=NotificationTypeChoices.SMS,
            title=kwargs.pop('title', 'Test SMS Notification'),
            body=kwargs.pop('body', 'This is a test SMS notification.'),
            url=kwargs.pop('url', ''),
            status=kwargs.pop('status', NotificationStatusChoices.PENDING),
            priority=kwargs.pop('priority', 'low'),
        )
        kwargs['notification'] = notification

    data = {
        'to_phone_number': '5551234567',
        'media_url': None,
        'temporary_media': None,
    }
    data.update(kwargs)
    return SmsNotification.objects.create(**data)

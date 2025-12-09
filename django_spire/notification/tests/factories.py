from __future__ import annotations

from django.contrib.auth.models import User

from django_spire.notification.choices import (
    NotificationPriorityChoices,
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.models import Notification


def create_test_notification(**kwargs) -> Notification:
    if 'user' not in kwargs:
        kwargs['user'] = User.objects.first()

    data = {
        'type': NotificationTypeChoices.APP,
        'title': 'Test Notification',
        'body': 'This is a test notification body.',
        'url': 'https://example.com',
        'status': NotificationStatusChoices.PENDING,
        'priority': NotificationPriorityChoices.LOW,
    }
    data.update(kwargs)
    return Notification.objects.create(**data)

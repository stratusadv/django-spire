from __future__ import annotations

from django.contrib.auth.models import User
from django.utils.timezone import now

from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.models import Notification


def create_test_app_notification(**kwargs) -> AppNotification:
    if 'notification' not in kwargs:
        user = kwargs.pop('user', None) or User.objects.first()
        notification = Notification.objects.create(
            user=user,
            type=NotificationTypeChoices.APP,
            title=kwargs.pop('title', 'Test App Notification'),
            body=kwargs.pop('body', 'This is a test app notification.'),
            url=kwargs.pop('url', 'https://example.com'),
            status=kwargs.pop('status', NotificationStatusChoices.SENT),
            priority=kwargs.pop('priority', 'low'),
            sent_datetime=kwargs.pop('sent_datetime', now()),
        )
        kwargs['notification'] = notification

    data = {
        'template': 'django_spire/notification/app/item/notification_item.html',
        'context_data': {},
    }
    data.update(kwargs)
    return AppNotification.objects.create(**data)

from __future__ import annotations

from django.contrib.auth.models import User

from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.models import Notification


def create_test_email_notification(**kwargs) -> EmailNotification:
    if 'notification' not in kwargs:
        user = kwargs.pop('user', None) or User.objects.first()
        notification = Notification.objects.create(
            user=user,
            type=NotificationTypeChoices.EMAIL,
            title=kwargs.pop('title', 'Test Email Notification'),
            body=kwargs.pop('body', 'This is a test email notification.'),
            url=kwargs.pop('url', 'https://example.com'),
            status=kwargs.pop('status', NotificationStatusChoices.PENDING),
            priority=kwargs.pop('priority', 'low'),
        )
        kwargs['notification'] = notification

    data = {
        'to_email_address': 'test@example.com',
        'template_id': '',
        'context_data': {},
        'cc': [],
        'bcc': [],
    }
    data.update(kwargs)
    return EmailNotification.objects.create(**data)

from __future__ import annotations

from abc import ABC, abstractmethod

from django_spire.notification.email import SendGridEmailHelper


class NotificationSender(ABC):
    def __init__(self, notification: 'Notification'):
        self.notification = notification

    @abstractmethod
    def send(self):
        pass


class EmailNotificationSender(NotificationSender):
    def send(self):
        template_data = {
            'title': self.notification.title,
            'body': self.notification.body,
            'name': self.notification.name,
            'button_url': self.notification.url,
        }
        SendGridEmailHelper(
            to=self.notification.email,
            template_data=template_data,
            fail_silently=False
        ).send()

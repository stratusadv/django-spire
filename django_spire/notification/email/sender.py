from __future__ import annotations

from abc import ABC, abstractmethod
from typing_extensions import TYPE_CHECKING

from django_spire.notification.email.helper import SendGridEmailHelper

if TYPE_CHECKING:
    from django_spire.notification.models import Notification


class NotificationSender(ABC):
    def __init__(self, notification: Notification):
        self.notification = notification

    @abstractmethod
    def send(self) -> None:
        raise NotImplementedError


class EmailNotificationSender(NotificationSender):
    def send(self) -> None:
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

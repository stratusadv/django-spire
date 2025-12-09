from __future__ import annotations

from abc import ABC, abstractmethod

from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.models import Notification


class BaseNotificationProcessor(ABC):
    @abstractmethod
    def process(self, notification: Notification):
        raise NotImplementedError

    @abstractmethod
    def process_list(self, notifications: list[Notification]):
        raise NotImplementedError

    @abstractmethod
    def process_ready(self):
        raise NotImplementedError

    @abstractmethod
    def process_errored(self):
        raise NotImplementedError

    @staticmethod
    def _update_notifications_to_processing(notifications: list[Notification]):
        for notification in notifications:
            notification.status = NotificationStatusChoices.PROCESSING

        Notification.objects.bulk_update(notifications, ['status'])

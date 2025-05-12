from abc import ABC, abstractmethod
from collections import defaultdict

from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.processor import EmailNotificationProcessor
from django_spire.notification.maps import NotificationProcessorMap
from django_spire.notification.models import Notification


class BaseNotificationProcessor(ABC):
    @abstractmethod
    def process(self, notification: Notification):
        raise NotImplementedError

    @abstractmethod
    def process_list(self, notifications: list[Notification]):
        raise NotImplementedError

    @abstractmethod
    def process_all(self):
        raise NotImplementedError

    @abstractmethod
    def process_errored(self):
        raise NotImplementedError


class NotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        NotificationProcessorMap(notification.type).value.process(notification)

    def process_list(self, notifications: list[Notification]):
        sorted_notifications = defaultdict(list)

        for notification in notifications:
            sorted_notifications[notification.type].append(notification)

        for notification_type, notifications in sorted_notifications.items():
            self._process_list_by_type(notification_type, notifications)

    @staticmethod
    def _process_list_by_type(
        notification_type: NotificationTypeChoices,
        notifications: list[Notification],
    ):
        if notification_type == NotificationTypeChoices.EMAIL:
            EmailNotificationProcessor().process_list(notifications)

    def process_all(self):
        self.process_list(Notification.objects.ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.errored().active())

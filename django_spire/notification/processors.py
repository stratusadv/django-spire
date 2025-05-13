from abc import ABC, abstractmethod
from collections import defaultdict

from django_spire.notification.choices import NotificationTypeChoices
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
        self._process_list_by_type(notification.type, [notification])

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
        if notification_type == NotificationTypeChoices.APP:
            from django_spire.notification.app.processor import AppNotificationProcessor
            AppNotificationProcessor().process_list(notifications)

        elif notification_type == NotificationTypeChoices.EMAIL:
            from django_spire.notification.email.processor import EmailNotificationProcessor
            EmailNotificationProcessor().process_list(notifications)

        elif notification_type == NotificationTypeChoices.PUSH:
            pass

        elif notification_type == NotificationTypeChoices.SMS:
            from django_spire.notification.sms.processor import SMSNotificationProcessor
            SMSNotificationProcessor().process_list(notifications)

        else:
            raise ValueError(f'Unknown notification type: {notification_type}')

    def process_all(self):
        self.process_list(Notification.objects.ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.errored().active())

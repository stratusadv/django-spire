from collections import defaultdict

from django_spire.notification.app.processor import AppNotificationProcessor
from django_spire.notification.choices import NotificationStatusChoices, \
    NotificationTypeChoices
from django_spire.notification.email.processor import EmailNotificationProcessor
from django_spire.notification.models import Notification
from django_spire.notification.processors.processor import BaseNotificationProcessor
from django_spire.notification.sms.processor import SMSNotificationProcessor


class NotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        processor = self._get_processor(notification.type)
        if processor is None:
            notification.status = NotificationStatusChoices.FAILED
            notification.save()
            raise ValueError(f'Unknown notification type: {notification.type}')

        processor().process(notification)

    def process_list(self, notifications: list[Notification]):
        sorted_notifications = defaultdict(list)

        for notification in notifications:
            sorted_notifications[notification.type].append(notification)

        for notification_type, notifications in sorted_notifications.items():
            processor = self._get_processor(notification_type)

            if processor is None:
                for notification in notifications:
                    notification.status = NotificationStatusChoices.FAILED

                Notification.objects.bulk_update(notifications, ['status'])
                continue

            processor().process_list(notifications)

    @staticmethod
    def _get_processor(
        notification_type: NotificationTypeChoices
    ) -> type[BaseNotificationProcessor] | None:
        if notification_type == NotificationTypeChoices.APP:
            return AppNotificationProcessor

        elif notification_type == NotificationTypeChoices.EMAIL:
            return EmailNotificationProcessor

        elif notification_type == NotificationTypeChoices.SMS:
            return SMSNotificationProcessor

        return None

    def process_ready(self):
        self.process_list(Notification.objects.ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.errored().active())

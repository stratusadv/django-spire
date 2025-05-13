from collections import defaultdict

from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.maps import NotificationProcessorMap
from django_spire.notification.models import Notification


class NotificationManager:
    @staticmethod
    def process(notification: Notification):
        processor = NotificationProcessorMap.get(notification.type)
        if processor is None:
            notification.status = NotificationStatusChoices.FAILED
            notification.save()
            raise ValueError(f'Unknown notification type: {notification.type}')

        processor().process(notification)

    @staticmethod
    def process_list(notifications: list[Notification]):
        sorted_notifications = defaultdict(list)

        for notification in notifications:
            sorted_notifications[notification.type].append(notification)

        for notification_type, notifications in sorted_notifications.items():
            processor = NotificationProcessorMap.get(notification_type)

            if processor is None:
                for notification in notifications:
                    notification.status = NotificationStatusChoices.FAILED

                Notification.objects.bulk_update(notifications, ['status'])
                continue

            processor().process_list(notifications)

    def process_all(self):
        self.process_list(Notification.objects.ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.errored().active())

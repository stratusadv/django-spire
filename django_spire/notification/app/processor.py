from django.utils.timezone import now

from django_spire.notification.choices import NotificationTypeChoices, \
    NotificationStatusChoices
from django_spire.notification.models import Notification
from django_spire.notification.processors.processor import BaseNotificationProcessor


class AppNotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        errors = []
        if notification.type != NotificationTypeChoices.APP:
            errors.append(
                ValueError("AppNotificationProcessor only processes APP notifications")
            )

        if notification.user_id is None:
            errors.append(
                ValueError("AppNotifications must have a user associated with them")
            )

        if errors:
            notification.status = NotificationStatusChoices.FAILED
            notification.save()
            raise ExceptionGroup("AppNotificationProcessor failed", errors)

        notification.status = NotificationStatusChoices.SENT
        notification.sent_datetime = now()

        notification.save()

    def process_list(self, notifications: list):
        for notification in notifications:
            if notification.type != NotificationTypeChoices.APP:
                notification.status = NotificationStatusChoices.FAILED
                continue

            if notification.user is None:
                notification.status = NotificationStatusChoices.FAILED
                continue

            notification.status = NotificationStatusChoices.SENT
            notification.sent_datetime = now()

        Notification.objects.bulk_update(notifications, ['status', 'sent_datetime'])

    def process_ready(self):
        self.process_list(Notification.objects.app_notifications().ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.app_notifications().errored().active())

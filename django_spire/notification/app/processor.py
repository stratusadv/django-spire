from django.utils.timezone import now

from django_spire.notification.app.exceptions import AppNotificationException
from django_spire.notification.choices import NotificationTypeChoices, \
    NotificationStatusChoices
from django_spire.notification.models import Notification
from django_spire.notification.processors.processor import BaseNotificationProcessor


class AppNotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        try:
            self._validate_notification_type(notification, NotificationTypeChoices.APP)
            self._validate_notification_has_user(notification)

        except Exception as e:
            notification.status = NotificationStatusChoices.ERRORED
            notification.status_message = str(e)
            notification.save()
            raise e

        notification.status = NotificationStatusChoices.SENT
        notification.sent_datetime = now()

        notification.save()

    def process_list(self, notifications: list):
        self._update_notifications_to_processing(notifications)

        for notification in notifications:
            try:
                self._validate_notification_type(
                    notification,
                    NotificationTypeChoices.APP
                )
                self._validate_notification_has_user(notification)

                notification.status = NotificationStatusChoices.SENT
                notification.sent_datetime = now()

            except Exception as e:
                notification.status = NotificationStatusChoices.ERRORED
                notification.status_message = str(e)

                Notification.objects.bulk_update(
                    notifications,
                    ['status', 'sent_datetime', 'status_message']
                )
                raise e

        Notification.objects.bulk_update(
            notifications,
            ['status', 'sent_datetime', 'status_message']
        )

    def process_ready(self):
        self.process_list(Notification.objects.app_notifications().ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.app_notifications().errored().active())

    @staticmethod
    def _validate_notification_has_user(notification: Notification):
        if notification.user_id is None:
            raise AppNotificationException(
                'AppNotifications must have a user associated with them'
            )

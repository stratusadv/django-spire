from django.utils.timezone import now
from sendgrid import SendGridException

from django_spire.notification.choices import NotificationTypeChoices, \
    NotificationStatusChoices
from django_spire.notification.email.helper import SendGridEmailHelper
from django_spire.notification.exceptions import NotificationException
from django_spire.notification.models import Notification
from django_spire.notification.processors.processor import BaseNotificationProcessor


class EmailNotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        notification.status = NotificationStatusChoices.PROCESSING
        notification.save()

        try:
            if notification.type != NotificationTypeChoices.EMAIL:
                raise NotificationException(
                    f"EmailNotificationProcessor only processes "
                    f"Email notifications. Was provided {notification.type}"
                )

            SendGridEmailHelper(notification).send()

            notification.status = NotificationStatusChoices.SENT
            notification.sent_datetime = now()
        except Exception as e:
            notification.status_message = str(e)
            if isinstance(e, SendGridException):
                notification.status = NotificationStatusChoices.ERRORED
            else:
                notification.status = NotificationStatusChoices.FAILED
                raise e
        finally:
            notification.save()

    def process_list(self, notifications: list):
        self._update_notifications_to_processing(notifications)

        for notification in notifications:
            try:
                if notification.type != NotificationTypeChoices.EMAIL:
                    raise NotificationException(
                        f"EmailNotificationProcessor only processes "
                        f"Email notifications. Was provided {notification.type}"
                    )

                SendGridEmailHelper(notification).send()

                notification.status = NotificationStatusChoices.SENT
                notification.sent_datetime = now()
            except Exception as e:
                notification.status_message = str(e)
                if isinstance(e, SendGridException):
                    notification.status = NotificationStatusChoices.ERRORED
                else:
                    notification.status = NotificationStatusChoices.FAILED
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
        self.process_list(
            Notification.objects.
            email_notifications()
            .ready_to_send()
            .active()
            .prefetch_related('email', 'email__attachment')
        )

    def process_errored(self):
        self.process_list(
            Notification.objects
            .email_notifications()
            .errored()
            .active()
            .prefetch_related('email', 'email__attachment')
        )

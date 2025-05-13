from django.utils.timezone import now

from django_spire.notification.choices import NotificationTypeChoices, \
    NotificationStatusChoices
from django_spire.notification.email.helper import SendGridEmailHelper
from django_spire.notification.models import Notification
from django_spire.notification.processors import BaseNotificationProcessor


class EmailNotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        if notification.type != NotificationTypeChoices.EMAIL:
            notification.status = NotificationStatusChoices.FAILED
            notification.save()
            raise ValueError("EmailNotificationProcessor only processes EMAIL notifications")

        notification.status = NotificationStatusChoices.PROCESSING
        notification.save()

        try:
            SendGridEmailHelper(
                to=notification.email.to_email_address,
                template_data={
                    "subject": notification.title,
                    "body": notification.body,
                    "link": notification.url,
                }
            ).send()

            notification.status = NotificationStatusChoices.SENT
            notification.sent_datetime = now()
        except:
            notification.status = NotificationStatusChoices.ERRORED

        notification.save()

    def process_list(self, notifications: list):
        for notification in notifications:
            if notification.type != NotificationTypeChoices.EMAIL:
                notification.status = NotificationStatusChoices.FAILED
                continue

            notification.status = NotificationStatusChoices.PROCESSING
            try:
                SendGridEmailHelper(
                    to=notification.email.to_email_address,
                    template_data={
                        "subject": notification.title,
                        "body": notification.body,
                        "link": notification.url,
                    },
                ).send()

                notification.status = NotificationStatusChoices.SENT
                notification.sent_datetime = now()
            except Exception:
                notification.status = NotificationStatusChoices.ERRORED

        Notification.objects.bulk_update(notifications, ['status', 'sent_datetime'])

    def process_all(self):
        self.process_list(Notification.objects.email_notifications().ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.email_notifications().errored().active())

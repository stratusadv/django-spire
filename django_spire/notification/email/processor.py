from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.helper import SendGridEmailHelper
from django_spire.notification.models import Notification
from django_spire.notification.processors import BaseNotificationProcessor


class EmailNotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        if notification.type != NotificationTypeChoices.EMAIL:
            raise ValueError("EmailNotificationProcessor only processes EMAIL notifications")

        SendGridEmailHelper(
            to=notification.email.to_email_address,
            template_data={
                "subject": notification.title,
                "body": notification.body,
            }
        ).send()

    def process_list(self, notifications: list):
        for notification in notifications:
            self.process(notification)

    def process_all(self):
        pass
        # self.process_list(Notification.objects.ready_to_send().active())

    def process_errored(self):
        pass
        # self.process_list(Notification.objects.errored().active())

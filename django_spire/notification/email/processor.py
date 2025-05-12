from django_spire.notification.models import Notification
from django_spire.notification.processors import BaseNotificationProcessor


class EmailNotificationProcessor(BaseNotificationProcessor):
    def process(
            self,
            notifications: list[Notification],
    ):
        pass
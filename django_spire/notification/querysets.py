from django.contrib.auth.models import User
from django.utils.timezone import now

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
    NotificationPriorityChoices,
)


class NotificationQuerySet(HistoryQuerySet):
    def app_notifications(self):
        return self.filter(type=NotificationTypeChoices.APP)

    def by_user(self, user: User):
        return self.filter(user=user)

    def email_notifications(self):
        return self.filter(type=NotificationTypeChoices.EMAIL)

    def errored(self):
        return self.filter(status=NotificationStatusChoices.ERRORED)

    def failed(self):
        return self.filter(status=NotificationStatusChoices.FAILED)

    def high_priority(self):
        return self.filter(priority=NotificationPriorityChoices.HIGH)

    def low_priority(self):
        return self.filter(priority=NotificationPriorityChoices.LOW)

    def medium_priority(self):
        return self.filter(priority=NotificationPriorityChoices.MEDIUM)

    def pending(self):
        return self.filter(status=NotificationStatusChoices.PENDING)

    def processing(self):
        return self.filter(status=NotificationStatusChoices.PROCESSING)

    def push_notifications(self):
        return self.filter(status=NotificationTypeChoices.PUSH)

    def ready_to_send(self):
        return self.pending().filter(publish_datetime__lte=now())

    def sent(self):
        return self.filter(status=NotificationStatusChoices.SENT)

    def sms_notifications(self):
        return self.filter(type=NotificationTypeChoices.SMS)

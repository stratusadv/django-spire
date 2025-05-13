from django.utils.timezone import now

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import NotificationStatusChoices, \
    NotificationTypeChoices


class NotificationQuerySet(HistoryQuerySet):
    def app_notifications(self):
        return self.filter(type=NotificationTypeChoices.APP)

    def email_notifications(self):
        return self.filter(type=NotificationTypeChoices.EMAIL)

    def errored(self):
        return self.filter(status=NotificationStatusChoices.ERRORED)

    def pending(self):
        return self.filter(status=NotificationStatusChoices.PENDING)

    def push_notifications(self):
        return self.filter(status=NotificationTypeChoices.PUSH)

    def ready_to_send(self):
        return self.pending().filter(publish_datetime__lte=now)

    def sms_notifications(self):
        return self.filter(type=NotificationTypeChoices.SMS)

from django.utils.timezone import now

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import NotificationStatusChoices


class NotificationQuerySet(HistoryQuerySet):
    def errored(self):
        return self.filter(status=NotificationStatusChoices.ERRORED)

    def pending(self):
        return self.filter(status=NotificationStatusChoices.PENDING)

    def ready_to_send(self):
        return self.pending().filter(publish_datetime__lte=now)


from __future__ import annotations

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.querysets import NotificationContentObjectQuerySet


class SmsNotificationQuerySet(HistoryQuerySet, NotificationContentObjectQuerySet):
    pass


class SmsTemporaryMediaQuerySet(HistoryQuerySet):
    def is_ready_for_deletion(self):
        return [media for media in self if media.is_ready_for_deletion()]

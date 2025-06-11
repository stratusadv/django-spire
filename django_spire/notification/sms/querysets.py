from django_spire.history.querysets import HistoryQuerySet


class SmsNotificationQuerySet(HistoryQuerySet):
    pass


class SmsTemporaryMediaQuerySet(HistoryQuerySet):
    def is_ready_for_deletion(self):
        return [media for media in self if media.is_ready_for_deletion()]

from __future__ import annotations

from django_spire.history.querysets import HistoryQuerySet


class SmsConversationQuerySet(HistoryQuerySet):
    def by_phone_number(self, phone_number: str):
        return self.filter(
            phone_number=phone_number,
        )


class SmsMessageQuerySet(HistoryQuerySet):
    def newest_by_count(self, count: int = 20):
        return self.order_by('-created_datetime')[:count]

    def newest_by_count_reversed(self, count: int = 20):
        return self.order_by('-created_datetime')[:count][::-1]

from __future__ import annotations

from typing import Self

from django_spire.history.querysets import HistoryQuerySet


class SmsConversationQuerySet(HistoryQuerySet):
    def by_phone_number(self, phone_number: str) -> Self:
        return self.filter(phone_number=phone_number)


class SmsMessageQuerySet(HistoryQuerySet):
    def inbound_by_twilio_sid(self, twilio_sid: str) -> Self:
        return self.filter(is_inbound=True, twilio_sid=twilio_sid)

    def newest_by_count(self, count: int = 20) -> Self:
        return self.order_by('-created_datetime')[:count]

    def newest_by_count_reversed(self, count: int = 20) -> Self:
        return self.order_by('-created_datetime')[:count][::-1]


class SmsPhoneNumberQuerySet(HistoryQuerySet):
    def verified_by_phone_number(self, phone_number: str) -> Self:
        return self.active().filter(is_verified=True, phone_number=phone_number)

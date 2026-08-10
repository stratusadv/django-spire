from __future__ import annotations

from typing import Self

from django_spire.history.querysets import HistoryQuerySet


class AuthSmsQuerySet(HistoryQuerySet):
    def verified_by_phone_number(self, phone_number: str) -> Self:
        return self.active().filter(is_verified=True, phone_number=phone_number)

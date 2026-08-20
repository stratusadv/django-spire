from __future__ import annotations

from typing import Self

from django.contrib.auth.models import User

from django_spire.history.querysets import HistoryQuerySet


class AuthSmsQuerySet(HistoryQuerySet):
    def by_phone_number(self, phone_number: str) -> Self:
        return self.filter(phone_number=phone_number)

    def by_user(self, user: User) -> Self:
        return self.filter(user=user)

    def is_verified(self) -> Self:
        return self.filter(is_verified=True)

from __future__ import annotations

from django.db.models import Q, Count

from django_spire.history.querysets import HistoryQuerySet
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ChatQuerySet(HistoryQuerySet):
    def by_user(self, user: User) -> Self:
        return self.filter(user=user)

    def get_empty_or_create(self, user: User) -> Self:
        try:
            return (
                self.filter(user=user)
                .annotate(num_messages=Count('message'))
                .filter(num_messages=0)
                .earliest('-id')
            )
        except self.model.DoesNotExist:
            return self.create(user=user)

    def search(self, query: str) -> Self:
        return self.filter(Q(name__icontains=query))


class ChatMessageQuerySet(HistoryQuerySet):
    def newest_by_count(self, count: int = 20) -> Self:
        return self.order_by('-created_datetime')[:count]

    def newest_by_count_reversed(self, count: int = 20) -> Self:
        return self.order_by('-created_datetime')[:count][::-1]

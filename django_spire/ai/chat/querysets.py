from __future__ import annotations

from django.db.models import Q, Count

from django_spire.history.querysets import HistoryQuerySet


class ChatQuerySet(HistoryQuerySet):
    def by_user(self, user):
        return self.filter(
            user=user,
        )

    def get_empty_or_create(self, user):
        try:
            return (
                self.filter(user=user)
                .annotate(num_messages=Count('message'))
                .filter(num_messages=0)
                .earliest('-id')
            )
        except self.model.DoesNotExist:
            return self.create(user=user)

    def search(self, query: str):
        return self.filter(
            Q(name__icontains=query)
        )


class ChatMessageQuerySet(HistoryQuerySet):
    def newest_by_count(self, count: int = 20):
        return self.order_by('-created_datetime')[:count]

    def newest_by_count_reversed(self, count: int = 20):
        return self.order_by('-created_datetime')[:count][::-1]

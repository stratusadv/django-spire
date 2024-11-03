from __future__ import annotations

from django.db.models import QuerySet


class ActivityQuerySet(QuerySet):
    def prefetch_user(self):
        return self.prefetch_related('user')


class HistoryQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

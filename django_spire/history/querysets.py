from __future__ import annotations

from django.db.models import QuerySet


class HistoryQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

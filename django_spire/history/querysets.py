from __future__ import annotations

from django.db.models import QuerySet


class HistoryQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)

    def inactive(self):
        return self.filter(is_active=False, is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def not_deleted(self):
        return self.filter(is_deleted=False)

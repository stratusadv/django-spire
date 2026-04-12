from __future__ import annotations

from django.db.models import QuerySet


class CeleryTaskQuerySet(QuerySet):
    def by_pending_and_reference_key(self, reference_key: str) -> QuerySet:
        return self.filter(reference_key=reference_key, status__in=('PENDING', 'STARTED', 'RETRY'))


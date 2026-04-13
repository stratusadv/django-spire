from __future__ import annotations

from celery import states
from django.db.models import QuerySet


class CeleryTaskQuerySet(QuerySet):
    def by_reference_key(self, reference_key: str) -> QuerySet:
        return self.filter(reference_key=reference_key)

    def by_unready(self) -> QuerySet:
        return self.filter(state__in=states.UNREADY_STATES)

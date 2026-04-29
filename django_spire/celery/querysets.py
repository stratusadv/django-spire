from __future__ import annotations

from celery import states
from django.db.models import QuerySet


class CeleryTaskQuerySet(QuerySet):
    def by_reference_keys(self, reference_keys: list[str]) -> QuerySet:
        return self.filter(reference_key__in=reference_keys)

    def by_unready(self) -> QuerySet:
        return self.filter(state__in=states.UNREADY_STATES)

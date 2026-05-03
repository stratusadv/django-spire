from __future__ import annotations

from celery import states
from django.db.models import QuerySet, Q


class CeleryTaskQuerySet(QuerySet):
    def by_model_keys(self, model_keys: list[str]) -> QuerySet:
        return self.filter(model_key__in=model_keys)

    def by_reference_keys(self, reference_keys: list[str]) -> QuerySet:
        return self.filter(reference_key__in=reference_keys)

    def by_reference_keys_model_keys(self, reference_keys_model_keys: dict[str, str | None]) -> QuerySet:
        query = Q()

        for reference_key, model_key in reference_keys_model_keys.items():
            if model_key is not None:
                query |= Q(reference_key=reference_key, model_key=model_key)
            else:
                query |= Q(reference_key=reference_key, model_key__isnull=True)

        return self.filter(query)

    def by_unready(self) -> QuerySet:
        return self.filter(state__in=states.UNREADY_STATES)
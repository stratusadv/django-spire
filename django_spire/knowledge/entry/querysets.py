from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.ordering.queryset_mixin import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django_spire.knowledge.entry.models import Entry


class EntryQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def has_current_version(self) -> QuerySet[Entry]:
        return self.filter(current_version__isnull=False)

    def id_in(self, ids: list[int]) -> QuerySet[Entry]:
        return self.filter(id__in=ids)

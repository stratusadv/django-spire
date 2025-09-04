from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.ordering.queryset_mixin import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def greater_or_equal_order(self, order: int) -> QuerySet[EntryVersionBlock]:
        return self.filter(order__gte=order)

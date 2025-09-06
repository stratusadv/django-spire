from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.ordering.querysets import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def by_version_id(self, entry_version_id: int) -> QuerySet[EntryVersionBlock]:
        return self.filter(version_id=entry_version_id)

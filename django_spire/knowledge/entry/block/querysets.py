from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django_spire.knowledge.entry.block.models import EntryVersionBlock


class EntryVersionBlockQuerySet(HistoryQuerySet):
    def greater_or_equal_order(self, version_block: EntryVersionBlock):
        return self.filter(order__gte=version_block.order).exclude(id=version_block.id)

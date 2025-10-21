from __future__ import annotations

from django.db.models import Prefetch

from django_spire.history.querysets import HistoryQuerySet


class EntryVersionQuerySet(HistoryQuerySet):
    def prefetch_blocks(self):
        from django_spire.knowledge.entry.version.block.models import EntryVersionBlock

        return self.prefetch_related(
            Prefetch(
                'blocks',
                queryset=EntryVersionBlock.objects.order_by('order')
            )
        )
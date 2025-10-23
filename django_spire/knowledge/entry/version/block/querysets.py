from __future__ import annotations

from django.db.models.functions import Coalesce
from django.db.models import JSONField

from django_spire.contrib.ordering.querysets import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet
from django.db.models import Value


class EntryVersionBlockQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def format_for_editor(self):
        coalesce_json_field = lambda field_name: Coalesce(
            field_name,
            Value({}, output_field=JSONField())
        )

        return (
            self.annotate(
                data=coalesce_json_field('_block_data'),
                tunes=coalesce_json_field('_tunes_data'),
            )
            .order_by('order')
            .values('id', 'type', 'data', 'tunes')
        )
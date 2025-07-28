from django_spire.contrib.ordering.queryset_mixin import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet


class EntryVersionBlockQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def greater_or_equal_order(self, order: int):
        return self.filter(order__gte=order)

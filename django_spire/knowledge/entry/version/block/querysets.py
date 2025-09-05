from django_spire.contrib.ordering.querysets import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet


class EntryVersionBlockQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    pass

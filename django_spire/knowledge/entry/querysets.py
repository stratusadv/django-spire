from django_spire.contrib.ordering.queryset_mixin import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet


class EntryQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def has_current_version(self):
        return self.filter(current_version__isnull=False)

from django_spire.history.querysets import HistoryQuerySet


class EntryVersionBlockQuerySet(HistoryQuerySet):
    def greater_or_equal_order(self, order: int):
        return self.filter(order__gte=order)

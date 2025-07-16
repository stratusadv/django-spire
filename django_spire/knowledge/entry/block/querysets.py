from django_spire.history.querysets import HistoryQuerySet


class EntryQuerySet(HistoryQuerySet):
    def has_current_version(self):
        return self.filter(current_version__isnull=False)


class EntryVersionQuerySet(HistoryQuerySet):
    pass

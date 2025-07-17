from django_spire.history.querysets import HistoryQuerySet


class EntryVersionBlockQuerySet(HistoryQuerySet):
    def by_collection(self, collection):
        return self.filter(collection=collection)

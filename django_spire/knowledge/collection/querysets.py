from django.db.models import Count

from django_spire.history.querysets import HistoryQuerySet


class CollectionQuerySet(HistoryQuerySet):
    def by_parent(self, parent):
        return self.filter(parent=parent)

    def childless(self):
        return self.annotate(
            child_count=Count('child')
        ).filter(child_count=0)

    def parentless(self):
        return self.annotate(
            parent_count=Count('parent')
        ).filter(parent_count=0)

from django.db.models import QuerySet


class GroupQuerySet(QuerySet):
    def active(self):
        return self.order_by('name')

from django.db.models import QuerySet


class ActivityQuerySet(QuerySet):
    def prefetch_user(self):
        return self.prefetch_related('user')

from django.db.models import QuerySet


class TaskQuerySet(QuerySet):

    def active(self):
        return self.filter(is_active=True, is_deleted=False)

    def complete(self):
        return self.filter(is_complete=True)

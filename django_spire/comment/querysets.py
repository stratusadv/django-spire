from django.db.models import QuerySet


class CommentQuerySet(QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def top_level(self):
        return self.filter(parent__isnull=True)

    def prefetch_user(self):
        return self.prefetch_related('user')

    def prefetch_parent(self):
        return self.prefetch_related('parent')

    def prefetch_replies(self):
        return self.prefetch_related('children')

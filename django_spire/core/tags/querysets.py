from django.db.models import QuerySet


class TagQuerySet(QuerySet):
    def in_tags_set(self, tags_set: set[str]):
        return self.filter(tags__name__in=tags_set)

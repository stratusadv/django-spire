from __future__ import annotations

from django.db.models import QuerySet
from django.utils.text import slugify


class TagQuerySet(QuerySet):
    def in_tag_set(self, tag_set: set[str]):
        slugified_tag_set = set(map(slugify, tag_set))

        return self.filter(name__in=slugified_tag_set)

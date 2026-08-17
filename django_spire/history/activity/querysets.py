from __future__ import annotations

from typing import Self

from django.db.models import QuerySet


class ActivityQuerySet(QuerySet):
    def prefetch_user(self) -> Self:
        return self.prefetch_related('user')

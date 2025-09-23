from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count

from django_spire.contrib.ordering.querysets import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django_spire.auth.user.models import AuthUser
    from django.db.models import QuerySet
    from django_spire.knowledge.collection.models import Collection


class CollectionQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def annotate_entry_count(self) -> QuerySet[Collection]:
        return self.annotate(entry_count=Count('entry'))

    def by_parent(self, parent: Collection) -> QuerySet[Collection]:
        return self.filter(parent=parent)

    def by_parent_id(self, parent_id: int) -> QuerySet[Collection]:
        return self.filter(parent_id=parent_id)

    def childless(self) -> QuerySet[Collection]:
        return self.annotate(child_count=Count('child')).filter(child_count=0)

    def parentless(self) -> QuerySet[Collection]:
        return self.filter(parent_id__isnull=True)

    def user_has_access(self, user: AuthUser) -> QuerySet[Collection]:
        return self.filter(group__auth_group__user=user).distinct()

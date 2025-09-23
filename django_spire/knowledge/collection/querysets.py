from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, Q

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
        direct_access = self.filter(group__auth_group__user=user)
        accessible_ids = set(direct_access.values_list('id', flat=True))

        current_level_ids = accessible_ids.copy()
        while current_level_ids:
            next_level = self.filter(parent_id__in=current_level_ids)
            new_ids = set(next_level.values_list('id', flat=True)) - accessible_ids

            if not new_ids:
                break

            accessible_ids.update(new_ids)
            current_level_ids = new_ids

        return self.filter(id__in=accessible_ids).distinct()

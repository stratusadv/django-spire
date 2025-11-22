from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.ordering.querysets import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.db.models import QuerySet
    from django_spire.knowledge.collection.models import Collection


class CollectionQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def annotate_entry_count(self) -> QuerySet[Collection]:
        return self.annotate(entry_count=Count('entry'))

    def by_parent(self, parent: Collection) -> QuerySet[Collection]:
        return self.filter(parent=parent)

    def by_parent_id(self, parent_id: int) -> QuerySet[Collection]:
        return self.filter(parent_id=parent_id)

    def by_parent_ids(self, parent_ids: list[int]) -> QuerySet[Collection]:
        return self.filter(parent_id__in=parent_ids)

    def childless(self) -> QuerySet[Collection]:
        return self.annotate(child_count=Count('child')).filter(child_count=0)

    def children(self, collection_id: int) -> QuerySet[Collection]:
        return self.filter(
            id__in=self.model.services.tool.get_children_ids(parent_id=collection_id)
        )

    def exclude_children(self, collection_id: int) -> QuerySet[Collection]:
        return self.exclude(
            id__in=self.model.services.tool.get_children_ids(parent_id=collection_id)
        )

    def parentless(self) -> QuerySet[Collection]:
        return self.filter(parent_id__isnull=True)

    def request_user_has_access(self, request: WSGIRequest) -> QuerySet[Collection]:
        user = request.user

        if user.is_superuser or AppAuthController('knowledge', request).can_access_all_collections():
            return self.all()

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

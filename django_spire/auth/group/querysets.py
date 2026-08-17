from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import GroupManager

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.auth.group.models import Group


class GroupQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def active(self):
        return self.order_by('name')

    # def bulk_filter(self, filter_data: dict) -> QuerySet[Group]:
    #     queryset = self
    #
    #     search = filter_data.get('search', '')
    #     if search:
    #         queryset = queryset.search(search)
    #
    #     return queryset


class AuthGroupManager(GroupManager.from_queryset(GroupQuerySet)):
    use_in_migrations = False

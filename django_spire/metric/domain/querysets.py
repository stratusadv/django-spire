from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.domain.models import Domain, SubDomain


class DomainQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[Domain]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset


class SubDomainQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def for_key(self, key: str) -> QuerySet[SubDomain]:
        return self.filter(key=key)

    def bulk_filter(self, filter_data: dict) -> QuerySet[SubDomain]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset

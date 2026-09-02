from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.visual.signage.models import Signage, SignagePresentation


class SignageQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[Signage]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset

    def for_key(self, key: str) -> QuerySet[Signage]:
        return self.filter(key=key, is_deleted=False)

    def with_presentations(self) -> QuerySet[Signage]:
        return self.prefetch_related(
            'signage_presentations',
            'signage_presentations__presentation',
            'signage_presentations__presentation__slides',
            'signage_presentations__presentation__slides__sections',
            'signage_presentations__presentation__slides__sections__visual',
        )


class SignagePresentationQuerySet(HistoryQuerySet):
    def for_signage(self, signage: Signage) -> QuerySet[SignagePresentation]:
        return self.filter(signage=signage)

    def with_presentation(self) -> QuerySet[SignagePresentation]:
        return self.select_related('presentation')

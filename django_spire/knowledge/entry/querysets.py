from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q

from django_spire.contrib.ordering.querysets import OrderingQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.auth.user.models import AuthUser
    from django_spire.knowledge.entry.models import Entry


class EntryQuerySet(HistoryQuerySet, OrderingQuerySetMixin):
    def get_by_version_block_id(self, version_block_id: int) -> Entry:
        return self.get(
            current_version__block__id=version_block_id
        )

    def has_current_version(self) -> QuerySet[Entry]:
        return self.filter(current_version__isnull=False)

    def id_in(self, ids: list[int]) -> QuerySet[Entry]:
        return self.filter(id__in=ids)

    def user_has_access(self, user: AuthUser) -> QuerySet[Entry]:
        return self.filter(
            Q(
                current_version__status=EntryVersionStatusChoices.PUBLISHED
            ) |
            Q(
                current_version__author=user,
                current_version__status=EntryVersionStatusChoices.DRAFT
            )
        )

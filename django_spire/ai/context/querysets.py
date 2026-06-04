from __future__ import annotations

from django_spire.history.querysets import HistoryQuerySet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.ai.context.models import Organization


class OrganizationQuerySet(HistoryQuerySet):
    def get_only_or_none(self) -> Organization | None:
        try:
            return self.earliest('id')
        except self.model.DoesNotExist:
            return None


class PeopleQuerySet(HistoryQuerySet):
    pass

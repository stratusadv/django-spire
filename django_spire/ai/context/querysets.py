from __future__ import annotations

from django_spire.history.querysets import HistoryQuerySet


class OrganizationQuerySet(HistoryQuerySet):
    def get_only_or_none(self):
        try:
            return self.earliest('id')
        except self.model.DoesNotExist:
            return None


class PeopleQuerySet(HistoryQuerySet):
    pass

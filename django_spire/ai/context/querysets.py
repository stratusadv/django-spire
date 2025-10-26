from __future__ import annotations

from django_spire.history.querysets import HistoryQuerySet


class OrganizationQuerySet(HistoryQuerySet):
    def get_only(self):
        return self.earliest('id')


class PeopleQuerySet(HistoryQuerySet):
    pass

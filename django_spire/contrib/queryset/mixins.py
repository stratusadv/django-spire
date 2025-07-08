from __future__ import annotations

from abc import abstractmethod

from django.db.models import QuerySet

from django_spire.contrib.session.base_session import BaseSession


class SessionQuerySetFilterMixin(QuerySet):

    def process_session_filter(
            self,
            session: BaseSession,
            data: dict
    ) -> QuerySet:
        # If there is data I want to update the session data with it.
        # On clear I want to remove all data.
        # process_queryset_fitler_session_data(session, data)
        print(data)
        return self._session_filter(session.data)

    @abstractmethod
    def _session_filter(self, session_data: dict) -> QuerySet:
        pass


class SearchQuerySetMixin(QuerySet):

    @abstractmethod
    def search(self, value: str | None) -> QuerySet:
        pass

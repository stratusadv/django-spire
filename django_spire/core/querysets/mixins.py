from __future__ import annotations

from abc import abstractmethod, ABC

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from django_spire.core.querysets.session import QuerySetFilterSession


class SessionQuerySetFilterMixin(QuerySet):

    def process_session_filter(
            self,
            request: WSGIRequest,
            session_key: str
    ) -> QuerySet:
        queryset_filter_session = QuerySetFilterSession(request, session_key)
        return self._session_filter(queryset_filter_session.data)

    @abstractmethod
    def _session_filter(self, session_data: dict) -> QuerySet:
        pass


class SearchQuerySetMixin(QuerySet):

    @abstractmethod
    def search(self, value: str | None) -> QuerySet:
        pass

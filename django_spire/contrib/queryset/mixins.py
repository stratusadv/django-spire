from __future__ import annotations

from abc import abstractmethod
from typing import Type

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.forms import Form

from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.session.controller import SessionController


class SessionFilterQuerySetMixin(QuerySet):

    def process_session_filter(
            self,
            request: WSGIRequest,
            session_key: str,
            form_class: Type[Form]
    ) -> QuerySet:
        # Session keys must match to process new queryset data
        if session_key != request.GET.get('session_filter_key'):
            return self

        action = request.GET.get('action')
        form = form_class(request.GET)

        if form.is_valid():
            session = SessionController(request=request, session_key=session_key)

            # Todo: Change actions into an enum
            if action == 'Clear':
                session.purge()
                return self

            # The user has manipulated the filter form.
            if any(form.cleaned_data.values()):

                for key, value in form.cleaned_data.items():
                    session.add_data(key, value)

            return self._session_filter(session.data)
        else:
            show_form_errors(request, form)
            return self

    @abstractmethod
    def _session_filter(self, session_data: dict) -> QuerySet:
        pass


class SearchQuerySetMixin(QuerySet):

    @abstractmethod
    def search(self, value: str | None) -> QuerySet:
        pass

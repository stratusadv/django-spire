from __future__ import annotations

from abc import abstractmethod
from typing import Type

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.forms import Form

from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.queryset.enums import SessionFilterActionEnum
from django_spire.contrib.session.controller import SessionController


class SessionFilterQuerySetMixin(QuerySet):

    def process_session_filter(
            self,
            request: WSGIRequest,
            session_key: str,
            form_class: Type[Form]
    ) -> QuerySet:
        # Session keys must match to process new queryset data

        action = request.GET.get('action')
        form = form_class(request.GET)

        if form.is_valid():
            session = SessionController(request=request, session_key=session_key)

            # Todo: Change actions into an enum
            if action == SessionFilterActionEnum.CLEAR.value:
                session.purge()
                return self

            # The user has submitted the filter form
            if action == SessionFilterActionEnum.FILTER.value and session_key == request.GET.get('session_filter_key'):

                # Update session data
                for key, value in form.cleaned_data.items():
                    session.add_data(key, value)

            return self.bulk_filter(session.data)
        else:
            show_form_errors(request, form)
            return self


    @abstractmethod
    def bulk_filter(self, filter_data: dict) -> QuerySet:
        pass


class SearchQuerySetMixin(QuerySet):

    @abstractmethod
    def search(self, value: str | None) -> QuerySet:
        pass

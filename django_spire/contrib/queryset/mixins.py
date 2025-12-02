from __future__ import annotations

import json
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
            form_class: Type[Form],
            is_from_body: bool = False,
    ) -> QuerySet:
        # Session keys must match to process new queryset data

        data = json.loads(request.body.decode('utf-8')) if is_from_body else request.GET

        try:
            action = SessionFilterActionEnum(data.get('action'))
        except ValueError:
            action = None

        form = form_class(data)

        if form.is_valid():
            session = SessionController(request=request, session_key=session_key)

            if action == SessionFilterActionEnum.CLEAR:
                session.purge()
                return self

            # Apply filters when the user submits the filter form
            if (
                    action == SessionFilterActionEnum.FILTER
                    and session_key == data.get('session_filter_key')
            ):

                # Update session data
                for key, value in form.cleaned_data.items():
                    session.add_data(key, value)

            # If the session is expired, return the unfiltered queryset
            if session.is_expired:
                return self

            # When no new filter data is applied and session is NOT yet expired,
            # return the original queryset
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

from __future__ import annotations

import json

from abc import abstractmethod
from typing import TYPE_CHECKING

from django.db.models import QuerySet, Q
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.queryset.enums import SessionFilterActionEnum
from django_spire.contrib.session.controller import SessionController

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.forms import Form


class SessionFilterQuerySetMixin(QuerySet):
    def process_session_filter(
        self,
        request: WSGIRequest,
        session_key: str,
        form_class: type[Form],
        is_from_body: bool = False
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

        show_form_errors(request, form)
        return self

    @abstractmethod
    def bulk_filter(self, filter_data: dict) -> QuerySet:
        pass


class SearchQuerySetMixin(QuerySet):
    def search(self, value: str | None) -> QuerySet:
        words = value.split(' ')

        filtered_query = self

        char_fields = [
            field.name for field in self.model._meta.fields
            if field.get_internal_type() == 'CharField'
        ]

        for word in words:
            or_conditions = Q()
            for field in char_fields:
                or_conditions |= Q(**{f"{field}__icontains": word})
            filtered_query = filtered_query.filter(or_conditions)

        return filtered_query


class ChoicesQueryMixin(QuerySet):
    def to_choices(self):
        return [
            (obj.pk, str(obj)) for obj in self
        ]

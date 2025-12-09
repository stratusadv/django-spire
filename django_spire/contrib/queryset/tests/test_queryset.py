from __future__ import annotations

from unittest.mock import MagicMock

from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models import QuerySet
from django.test import RequestFactory, TestCase

from django_spire.contrib.queryset.enums import SessionFilterActionEnum
from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map
from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionFilterQuerySetMixin


class TestSessionFilterActionEnum(TestCase):
    def test_clear_value(self) -> None:
        assert SessionFilterActionEnum.CLEAR == 'Clear'

    def test_filter_value(self) -> None:
        assert SessionFilterActionEnum.FILTER == 'Filter'

    def test_is_str_enum(self) -> None:
        assert isinstance(SessionFilterActionEnum.CLEAR, str)
        assert isinstance(SessionFilterActionEnum.FILTER, str)


class TestFilterByLookupMap(TestCase):
    def setUp(self) -> None:
        self.queryset = MagicMock(spec=QuerySet)
        self.queryset.filter.return_value = self.queryset

    def test_applies_filter_from_lookup_map(self) -> None:
        lookup_map = {'name': 'name__icontains'}
        data = {'name': 'test'}

        filter_by_lookup_map(self.queryset, lookup_map, data)

        self.queryset.filter.assert_called_once_with(name__icontains='test')

    def test_extra_filters_applied(self) -> None:
        lookup_map = {'name': 'name__icontains'}
        data = {'name': 'test'}
        extra_filters = {'is_active': True}

        filter_by_lookup_map(self.queryset, lookup_map, data, extra_filters)

        self.queryset.filter.assert_called_once_with(
            name__icontains='test',
            is_active=True
        )

    def test_extra_filters_defaults_to_empty_dict(self) -> None:
        lookup_map = {}
        data = {}

        filter_by_lookup_map(self.queryset, lookup_map, data)

        self.queryset.filter.assert_called_once_with()

    def test_ignores_empty_string_values(self) -> None:
        lookup_map = {'name': 'name__icontains', 'email': 'email__icontains'}
        data = {'name': 'test', 'email': ''}

        filter_by_lookup_map(self.queryset, lookup_map, data)

        self.queryset.filter.assert_called_once_with(name__icontains='test')

    def test_ignores_keys_not_in_lookup_map(self) -> None:
        lookup_map = {'name': 'name__icontains'}
        data = {'name': 'test', 'other': 'value'}

        filter_by_lookup_map(self.queryset, lookup_map, data)

        self.queryset.filter.assert_called_once_with(name__icontains='test')

    def test_ignores_none_values(self) -> None:
        lookup_map = {'name': 'name__icontains', 'email': 'email__icontains'}
        data = {'name': 'test', 'email': None}

        filter_by_lookup_map(self.queryset, lookup_map, data)

        self.queryset.filter.assert_called_once_with(name__icontains='test')

    def test_ignores_empty_list_values(self) -> None:
        lookup_map = {'name': 'name__icontains', 'tags': 'tags__in'}
        data = {'name': 'test', 'tags': []}

        filter_by_lookup_map(self.queryset, lookup_map, data)

        self.queryset.filter.assert_called_once_with(name__icontains='test')

    def test_multiple_filters_applied(self) -> None:
        lookup_map = {'name': 'name__icontains', 'status': 'status'}
        data = {'name': 'test', 'status': 'active'}

        filter_by_lookup_map(self.queryset, lookup_map, data)

        self.queryset.filter.assert_called_once_with(
            name__icontains='test',
            status='active'
        )

    def test_returns_filtered_queryset(self) -> None:
        lookup_map = {'name': 'name__icontains'}
        data = {'name': 'test'}

        result = filter_by_lookup_map(self.queryset, lookup_map, data)

        assert result == self.queryset


class TestSessionFilterQuerySetMixin(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def _create_request_with_session(self, path: str = '/', data: dict | None = None):
        request = self.factory.get(path, data or {})
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_has_bulk_filter_abstract_method(self) -> None:
        assert hasattr(SessionFilterQuerySetMixin, 'bulk_filter')

    def test_has_process_session_filter_method(self) -> None:
        assert hasattr(SessionFilterQuerySetMixin, 'process_session_filter')

    def test_is_queryset_subclass(self) -> None:
        assert issubclass(SessionFilterQuerySetMixin, QuerySet)


class TestSearchQuerySetMixin(TestCase):
    def test_has_search_abstract_method(self) -> None:
        assert hasattr(SearchQuerySetMixin, 'search')

    def test_is_queryset_subclass(self) -> None:
        assert issubclass(SearchQuerySetMixin, QuerySet)

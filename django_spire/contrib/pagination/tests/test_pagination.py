from __future__ import annotations

from unittest.mock import MagicMock

from django.core.paginator import Page
from django.test import RequestFactory, TestCase

from django_spire.contrib.pagination.pagination import paginate_list
from django_spire.contrib.pagination.templatetags.pagination_tags import (
    get_elided_page_range,
    pagination_url,
)


class TestPaginateList(TestCase):
    def setUp(self) -> None:
        self.object_list = list(range(100))

    def test_custom_page_number(self) -> None:
        result = paginate_list(self.object_list, page_number=2)

        assert result.number == 2

    def test_custom_per_page(self) -> None:
        result = paginate_list(self.object_list, per_page=10)

        assert len(result.object_list) == 10

    def test_default_page_number(self) -> None:
        result = paginate_list(self.object_list)

        assert result.number == 1

    def test_default_per_page(self) -> None:
        result = paginate_list(self.object_list)

        assert len(result.object_list) == 50

    def test_empty_list(self) -> None:
        result = paginate_list([])

        assert len(result.object_list) == 0

    def test_has_next_page(self) -> None:
        result = paginate_list(self.object_list, page_number=1)

        assert result.has_next() is True

    def test_has_previous_page(self) -> None:
        result = paginate_list(self.object_list, page_number=2)

        assert result.has_previous() is True

    def test_last_page_has_no_next(self) -> None:
        result = paginate_list(self.object_list, page_number=2)

        assert result.has_next() is False

    def test_page_number_exceeds_pages_returns_last_page(self) -> None:
        result = paginate_list(self.object_list, page_number=999)

        assert result.number == 2

    def test_returns_page_object(self) -> None:
        result = paginate_list(self.object_list)

        assert isinstance(result, Page)


class TestPaginationUrl(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def _create_context(self, request) -> MagicMock:
        context = MagicMock()
        context.request = request
        return context

    def test_custom_page_name(self) -> None:
        request = self.factory.get('/')
        context = self._create_context(request)

        result = pagination_url(context, page_number=2, page_name='p')

        assert 'p=2' in result

    def test_default_page_name(self) -> None:
        request = self.factory.get('/')
        context = self._create_context(request)

        result = pagination_url(context, page_number=1)

        assert 'page=1' in result

    def test_multiple_query_params(self) -> None:
        request = self.factory.get('/', {'filter': 'active', 'sort': 'name'})
        context = self._create_context(request)

        result = pagination_url(context, page_number=3)

        assert 'page=3' in result
        assert 'filter=active' in result
        assert 'sort=name' in result

    def test_preserves_existing_query_params(self) -> None:
        request = self.factory.get('/', {'search': 'test'})
        context = self._create_context(request)

        result = pagination_url(context, page_number=2)

        assert 'search=test' in result
        assert 'page=2' in result

    def test_replaces_space_with_plus(self) -> None:
        request = self.factory.get('/', {'search': 'hello world'})
        context = self._create_context(request)

        result = pagination_url(context, page_number=1)

        assert 'search=hello+world' in result

    def test_returns_query_string(self) -> None:
        request = self.factory.get('/')
        context = self._create_context(request)

        result = pagination_url(context, page_number=1)

        assert result.startswith('?')


class TestGetElidedPageRange(TestCase):
    def test_custom_on_each_side(self) -> None:
        page_obj = MagicMock()
        page_obj.number = 5
        page_obj.paginator.get_elided_page_range.return_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        get_elided_page_range(page_obj, on_each_side=3)

        page_obj.paginator.get_elided_page_range.assert_called_once_with(
            number=5,
            on_each_side=3,
            on_ends=2
        )

    def test_custom_on_ends(self) -> None:
        page_obj = MagicMock()
        page_obj.number = 5
        page_obj.paginator.get_elided_page_range.return_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        get_elided_page_range(page_obj, on_ends=3)

        page_obj.paginator.get_elided_page_range.assert_called_once_with(
            number=5,
            on_each_side=2,
            on_ends=3
        )

    def test_default_parameters(self) -> None:
        page_obj = MagicMock()
        page_obj.number = 1
        page_obj.paginator.get_elided_page_range.return_value = [1, 2, 3]

        get_elided_page_range(page_obj)

        page_obj.paginator.get_elided_page_range.assert_called_once_with(
            number=1,
            on_each_side=2,
            on_ends=2
        )

    def test_returns_elided_page_range(self) -> None:
        page_obj = MagicMock()
        page_obj.number = 1
        expected_range = [1, 2, 3, '...', 10]
        page_obj.paginator.get_elided_page_range.return_value = expected_range

        result = get_elided_page_range(page_obj)

        assert result == expected_range

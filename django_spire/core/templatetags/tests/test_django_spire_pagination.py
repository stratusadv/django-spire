from __future__ import annotations

import unittest

from unittest.mock import MagicMock

from django.template import Context, Template

from django_spire.core.templatetags.django_spire_pagination import (
    get_elided_page_range,
    pagination_url,
)


class TestPaginationUrl(unittest.TestCase):
    def test_builds_query_string_with_single_param(self) -> None:
        class DummyContext:
            class request:  # noqa: N801
                GET = {'page': '1'}

        result = pagination_url(DummyContext(), 2)

        assert result == '?page=2'

    def test_builds_query_string_with_multiple_params(self) -> None:
        class DummyContext:
            class request:  # noqa: N801
                GET = {'page': '1', 'sort': 'name'}

        result = pagination_url(DummyContext(), 2)

        assert '?page=2' in result
        assert 'sort=name' in result

    def test_replaces_existing_page_param(self) -> None:
        class DummyContext:
            class request:  # noqa: N801
                GET = {'page': '5', 'filter': 'active'}

        result = pagination_url(DummyContext(), 10)

        assert 'page=10' in result
        assert 'page=5' not in result

    def test_handles_empty_get_params(self) -> None:
        class DummyContext:
            class request:  # noqa: N801
                GET = {}

        result = pagination_url(DummyContext(), 1)

        assert result == '?page=1'

    def test_preserves_non_page_params(self) -> None:
        class DummyContext:
            class request:  # noqa: N801
                GET = {'search': 'test query', 'category': 'books'}

        result = pagination_url(DummyContext(), 3)

        assert 'search=test+query' in result
        assert 'category=books' in result

    def test_custom_page_param_name(self) -> None:
        class DummyContext:
            class request:  # noqa: N801
                GET = {'p': '1'}

        result = pagination_url(DummyContext(), 2, page_name='p')

        assert result == '?p=2'

    def test_spaces_replaced_with_plus(self) -> None:
        class DummyContext:
            class request:  # noqa: N801
                GET = {'search': 'hello world'}

        result = pagination_url(DummyContext(), 1)

        assert 'search=hello+world' in result


class TestGetElidedPageRange(unittest.TestCase):
    def test_returns_iterator(self) -> None:
        mock_page = MagicMock()
        mock_page.number = 5
        mock_page.paginator.get_elided_page_range.return_value = iter([1, 2, 3, 4, 5, 6, 7])

        result = get_elided_page_range(mock_page)

        assert hasattr(result, '__iter__')

    def test_calls_paginator_method(self) -> None:
        mock_page = MagicMock()
        mock_page.number = 5
        mock_page.paginator.get_elided_page_range.return_value = iter([])

        list(get_elided_page_range(mock_page))

        mock_page.paginator.get_elided_page_range.assert_called_once_with(
            number=5, on_each_side=2, on_ends=2
        )

    def test_custom_elision_params(self) -> None:
        mock_page = MagicMock()
        mock_page.number = 10
        mock_page.paginator.get_elided_page_range.return_value = iter([])

        list(get_elided_page_range(mock_page, on_each_side=3, on_ends=1))

        mock_page.paginator.get_elided_page_range.assert_called_once_with(
            number=10, on_each_side=3, on_ends=1
        )


class TestPaginationTemplateRendering(unittest.TestCase):
    def test_render_pagination_url(self) -> None:
        template_code = """
            {% load django_spire_pagination %}

            {% pagination_url 2 as page_url %}
            {{ page_url }}
        """

        tmpl = Template(template_code)
        context = Context({})
        context.request = MagicMock()
        context.request.GET = {'page': '1'}
        rendered = tmpl.render(context)

        assert '?page=2' in rendered

    def test_render_get_elided_page_range(self) -> None:
        template_code = """
            {% load django_spire_pagination %}

            {% get_elided_page_range page_obj as page_range %}
            {% for p in page_range %}{{ p }}{% endfor %}
        """

        tmpl = Template(template_code)
        mock_page = MagicMock()
        mock_page.number = 5
        mock_page.paginator.get_elided_page_range.return_value = iter([1, 2, 3, 4, 5, 6, 7])
        context = Context({'page_obj': mock_page})
        rendered = tmpl.render(context)

        assert '1234567' in rendered

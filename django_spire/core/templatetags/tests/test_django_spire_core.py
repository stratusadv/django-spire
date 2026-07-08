from __future__ import annotations

import re
import string
import unittest
from unittest.mock import patch

from django.template import Context, Template
from django.template import RequestContext
from django.test import RequestFactory

from django_spire.core.templatetags.django_spire_core import (
    add_str,
    content_type_url,
    generate_id,
    in_list,
    index,
    is_path,
    not_in_list,
    query_param_url,
    safe_dict_items,
    to_snake_case as core_to_snake_case,
)


class TestAddStr(unittest.TestCase):
    def test_concatenates_strings(self) -> None:
        assert add_str('Hello', 'World') == 'HelloWorld'

    def test_empty_strings(self) -> None:
        assert add_str('', '') == ''

    def test_with_spaces(self) -> None:
        assert add_str('Hello ', 'World') == 'Hello World'


class TestContentTypeUrl(unittest.TestCase):
    def test_constructs_url_with_metadata(self) -> None:
        class Dummy:
            pass

        dummy = Dummy()
        dummy._meta = type('meta', (), {'app_label': 'myapp', 'model_name': 'dummy'})

        func = 'django_spire.core.templatetags.django_spire_core.reverse'
        return_value = 'http://example.com/dummy'

        with patch(func, return_value=return_value) as mock_reverse:
            url = content_type_url('dummy_url', dummy)

            mock_reverse.assert_called_once_with(
                'dummy_url', kwargs={'app_label': 'myapp', 'model_name': 'dummy'}
            )

            assert url == 'http://example.com/dummy'


class TestGenerateId(unittest.TestCase):
    def test_generates_8_characters(self) -> None:
        identifier = generate_id()
        assert len(identifier) == 8

    def test_only_ascii_letters(self) -> None:
        identifier = generate_id()
        assert all(ch in string.ascii_letters for ch in identifier)

    def test_unique_ids(self) -> None:
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100


class TestInList(unittest.TestCase):
    def test_empty_list(self) -> None:
        assert in_list('a', '') is False

    def test_value_in_list(self) -> None:
        assert in_list('a', 'a,b,c') is True

    def test_value_not_in_list(self) -> None:
        assert in_list('d', 'a,b,c') is False


class TestIndex(unittest.TestCase):
    def test_index_out_of_bounds(self) -> None:
        items = [10, 20, 30]
        assert index(items, 5) == items

    def test_negative_index(self) -> None:
        items = [10, 20, 30]
        assert index(items, -1) == 30

    def test_valid_index(self) -> None:
        items = [10, 20, 30]
        assert index(items, 1) == 20


class TestIsPath(unittest.TestCase):
    def test_empty_current(self) -> None:
        assert is_path('', '/test') is False

    def test_empty_url(self) -> None:
        assert is_path('/test', '') is False

    def test_exact_match(self) -> None:
        assert is_path('/test', '/test') is True

    def test_root_url(self) -> None:
        assert is_path('/test', '/') is False

    def test_starts_with(self) -> None:
        assert is_path('/test/page', '/test') is True


class TestNotInList(unittest.TestCase):
    def test_empty_list(self) -> None:
        assert not_in_list('a', '') is True

    def test_value_in_list(self) -> None:
        assert not_in_list('a', 'a,b,c') is False

    def test_value_not_in_list(self) -> None:
        assert not_in_list('x', 'a,b,c') is True


class TestSafeDictItems(unittest.TestCase):
    def test_dict_with_items_key(self) -> None:
        d = {'items': 'value', 'other': 'data'}
        result = list(safe_dict_items(d))

        assert ('items', 'value') in result
        assert ('other', 'data') in result

    def test_no_items_attribute(self) -> None:
        result = safe_dict_items('not a dict')
        assert result == []

    def test_normal_dict(self) -> None:
        d = {'key': 'value'}
        result = list(safe_dict_items(d))

        assert result == [('key', 'value')]


class TestToSnakeCaseCore(unittest.TestCase):
    def test_already_snake_case(self) -> None:
        assert core_to_snake_case('hello_world') == 'hello_world'

    def test_multiple_spaces(self) -> None:
        assert core_to_snake_case('Hello World Test') == 'hello_world_test'

    def test_simple_conversion(self) -> None:
        assert core_to_snake_case('Hello World') == 'hello_world'


class TestQueryParamUrl(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_multiple_params(self) -> None:
        request = self.factory.get('/some_path', {'foo': 'bar', 'baz': 'qux'})
        context = RequestContext(request, {})

        func = 'django_spire.core.templatetags.django_spire_core.reverse'
        return_value = 'http://example.com/dummy'

        with patch(func, return_value=return_value) as mock_reverse:
            url = query_param_url(context, 'dummy_url')
            mock_reverse.assert_called_once_with('dummy_url', kwargs={})

            assert url.startswith('http://example.com/dummy?')
            assert 'foo=bar' in url
            assert 'baz=qux' in url

    def test_no_params(self) -> None:
        request = self.factory.get('/some_path')
        context = RequestContext(request, {})

        func = 'django_spire.core.templatetags.django_spire_core.reverse'
        return_value = 'http://example.com/dummy'

        with patch(func, return_value=return_value):
            url = query_param_url(context, 'dummy_url')

            assert url == 'http://example.com/dummy?'


class TestDjangoSpireCoreTemplateRendering(unittest.TestCase):
    def test_render_add_str_filter(self) -> None:
        template_code = """
            {% load django_spire_core %}

            {{ "Hello" | add_str:" World" }}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert 'Hello World' in rendered

    def test_render_to_snake_case_tag(self) -> None:
        template_code = """
            {% load django_spire_core %}

            {% to_snake_case "Hello World" as snake_case %}
            {{ snake_case }}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert 'hello_world' in rendered

    def test_render_generate_id(self) -> None:
        template_code = """
            {% load django_spire_core %}

            {% generate_id as new_id %}
            {% generate_id as new_id2 %}
            <span id="{{ new_id }}"></span>
            <span id="{{ new_id2 }}"></span>
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())

        ids = re.findall(r'id="([A-Za-z]{8})"', rendered)
        assert len(ids) == 2
        assert ids[0] != ids[1]

    def test_render_in_list_filter(self) -> None:
        template_code = """
            {% load django_spire_core %}

            {% if "b"|in_list:"a,b,c" %}
                found
            {% else %}
                not found
            {% endif %}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert 'found' in rendered

    def test_render_not_in_list_filter(self) -> None:
        template_code = """
            {% load django_spire_core %}

            {% if "x"|not_in_list:"a,b,c" %}
                not in list
            {% else %}
                in list
            {% endif %}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert 'not in list' in rendered

    def test_render_index_filter(self) -> None:
        template_code = """
            {% load django_spire_core %}

            {{ items | index:1 }}
        """

        tmpl = Template(template_code)
        context = Context({'items': ['a', 'b', 'c']})
        rendered = tmpl.render(context)
        assert 'b' in rendered

    def test_render_safe_dict_items_filter(self) -> None:
        template_code = """
            {% load django_spire_core %}

            {% with my_dict|safe_dict_items as items %}
                {% for k, v in items %}{{ k }}:{{ v }}{% endfor %}
            {% endwith %}
        """

        tmpl = Template(template_code)
        context = Context({'my_dict': {'key': 'val', 'other': 'data'}})
        rendered = tmpl.render(context)
        assert 'key:val' in rendered
        assert 'other:data' in rendered

from __future__ import annotations

import json
import string

from unittest.mock import MagicMock, patch

from django.template import Context, RequestContext, Template
from django.test import RequestFactory, TestCase

from django_spire.core.templatetags.json import to_json
from django_spire.core.templatetags.message import django_messages_to_json
from django_spire.core.templatetags.spire_core_tags import (
    add_str,
    content_type_url,
    generate_id,
    in_list,
    index,
    is_path,
    not_in_list,
    query_param_url,
    safe_dict_items,
    to_snake_case,
)
from django_spire.core.templatetags.string_formating import (
    dashes_and_spaces_to_underscore,
    dashes_to_underscore,
    spaces_to_underscore,
    underscores_to_spaces,
)
from django_spire.core.templatetags.variable_types import (
    is_dict,
    is_list,
    is_list_or_tuple,
    is_not_dict,
    is_not_list,
    is_not_list_or_tuple,
    is_not_tuple,
    is_tuple,
)


class TestAddStr(TestCase):
    def test_concatenates_strings(self) -> None:
        assert add_str('Hello', 'World') == 'HelloWorld'

    def test_empty_strings(self) -> None:
        assert add_str('', '') == ''

    def test_with_spaces(self) -> None:
        assert add_str('Hello ', 'World') == 'Hello World'


class TestContentTypeUrl(TestCase):
    def test_constructs_url_with_metadata(self) -> None:
        class Dummy:
            pass

        dummy = Dummy()
        dummy._meta = type(
            'meta',
            (),
            {'app_label': 'myapp', 'model_name': 'dummy'}
        )

        func = 'django_spire.core.templatetags.spire_core_tags.reverse'
        return_value = 'http://example.com/dummy'

        with patch(func, return_value=return_value) as mock_reverse:
            url = content_type_url('dummy_url', dummy)

            mock_reverse.assert_called_once_with(
                'dummy_url',
                kwargs={'app_label': 'myapp', 'model_name': 'dummy'}
            )

            assert url == 'http://example.com/dummy'


class TestDashesAndSpacesToUnderscore(TestCase):
    def test_dashes_and_spaces(self) -> None:
        assert dashes_and_spaces_to_underscore('hello-world test') == 'hello_world_test'

    def test_no_changes_needed(self) -> None:
        assert dashes_and_spaces_to_underscore('hello_world') == 'hello_world'

    def test_only_dashes(self) -> None:
        assert dashes_and_spaces_to_underscore('hello-world') == 'hello_world'

    def test_only_spaces(self) -> None:
        assert dashes_and_spaces_to_underscore('hello world') == 'hello_world'


class TestDashesToUnderscore(TestCase):
    def test_multiple_dashes(self) -> None:
        assert dashes_to_underscore('hello-world-test') == 'hello_world_test'

    def test_no_dashes(self) -> None:
        assert dashes_to_underscore('hello') == 'hello'

    def test_single_dash(self) -> None:
        assert dashes_to_underscore('hello-world') == 'hello_world'


class TestDjangoMessagesToJson(TestCase):
    def test_empty_messages(self) -> None:
        result = django_messages_to_json([])
        assert json.loads(result) == []

    def test_multiple_messages(self) -> None:
        messages = [
            MagicMock(message='First', level_tag='info'),
            MagicMock(message='Second', level_tag='error'),
        ]

        result = django_messages_to_json(messages)
        parsed = json.loads(result)

        assert len(parsed) == 2
        assert parsed[0]['message'] == 'First'
        assert parsed[0]['type'] == 'info'
        assert parsed[1]['message'] == 'Second'
        assert parsed[1]['type'] == 'error'

    def test_single_message(self) -> None:
        messages = [MagicMock(message='Test message', level_tag='success')]

        result = django_messages_to_json(messages)
        parsed = json.loads(result)

        assert len(parsed) == 1
        assert parsed[0]['message'] == 'Test message'
        assert parsed[0]['type'] == 'success'
        assert len(parsed[0]['id']) == 8


class TestGenerateId(TestCase):
    def test_generates_8_characters(self) -> None:
        identifier = generate_id()
        assert len(identifier) == 8

    def test_only_ascii_letters(self) -> None:
        identifier = generate_id()
        assert all(ch in string.ascii_letters for ch in identifier)

    def test_unique_ids(self) -> None:
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100


class TestInList(TestCase):
    def test_empty_list(self) -> None:
        assert in_list('a', '') is False

    def test_value_in_list(self) -> None:
        assert in_list('a', 'a,b,c') is True

    def test_value_not_in_list(self) -> None:
        assert in_list('d', 'a,b,c') is False


class TestIndex(TestCase):
    def test_index_out_of_bounds(self) -> None:
        items = [10, 20, 30]
        assert index(items, 5) == items

    def test_negative_index(self) -> None:
        items = [10, 20, 30]
        assert index(items, -1) == 30

    def test_valid_index(self) -> None:
        items = [10, 20, 30]
        assert index(items, 1) == 20


class TestIsDict(TestCase):
    def test_dict(self) -> None:
        assert is_dict({'key': 'value'}) is True

    def test_empty_dict(self) -> None:
        assert is_dict({}) is True

    def test_list(self) -> None:
        assert is_dict([]) is False

    def test_string(self) -> None:
        assert is_dict('string') is False


class TestIsList(TestCase):
    def test_dict(self) -> None:
        assert is_list({}) is False

    def test_empty_list(self) -> None:
        assert is_list([]) is True

    def test_list(self) -> None:
        assert is_list([1, 2, 3]) is True

    def test_tuple(self) -> None:
        assert is_list((1, 2, 3)) is False


class TestIsListOrTuple(TestCase):
    def test_dict(self) -> None:
        assert is_list_or_tuple({}) is False

    def test_list(self) -> None:
        assert is_list_or_tuple([1, 2, 3]) is True

    def test_string(self) -> None:
        assert is_list_or_tuple('string') is False

    def test_tuple(self) -> None:
        assert is_list_or_tuple((1, 2, 3)) is True


class TestIsNotDict(TestCase):
    def test_dict(self) -> None:
        assert is_not_dict({'key': 'value'}) is False

    def test_list(self) -> None:
        assert is_not_dict([]) is True

    def test_string(self) -> None:
        assert is_not_dict('string') is True


class TestIsNotList(TestCase):
    def test_dict(self) -> None:
        assert is_not_list({}) is True

    def test_list(self) -> None:
        assert is_not_list([1, 2, 3]) is False

    def test_tuple(self) -> None:
        assert is_not_list((1, 2, 3)) is True


class TestIsNotListOrTuple(TestCase):
    def test_dict(self) -> None:
        assert is_not_list_or_tuple({}) is True

    def test_list(self) -> None:
        assert is_not_list_or_tuple([1, 2, 3]) is False

    def test_string(self) -> None:
        assert is_not_list_or_tuple('string') is True

    def test_tuple(self) -> None:
        assert is_not_list_or_tuple((1, 2, 3)) is False


class TestIsNotTuple(TestCase):
    def test_list(self) -> None:
        assert is_not_tuple([1, 2, 3]) is True

    def test_tuple(self) -> None:
        assert is_not_tuple((1, 2, 3)) is False


class TestIsPath(TestCase):
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


class TestIsTuple(TestCase):
    def test_list(self) -> None:
        assert is_tuple([1, 2, 3]) is False

    def test_tuple(self) -> None:
        assert is_tuple((1, 2, 3)) is True


class TestNotInList(TestCase):
    def test_empty_list(self) -> None:
        assert not_in_list('a', '') is True

    def test_value_in_list(self) -> None:
        assert not_in_list('a', 'a,b,c') is False

    def test_value_not_in_list(self) -> None:
        assert not_in_list('x', 'a,b,c') is True


class TestQueryParamUrl(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_multiple_params(self) -> None:
        request = self.factory.get('/some_path', {'foo': 'bar', 'baz': 'qux'})
        context = RequestContext(request, {})

        func = 'django_spire.core.templatetags.spire_core_tags.reverse'
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

        func = 'django_spire.core.templatetags.spire_core_tags.reverse'
        return_value = 'http://example.com/dummy'

        with patch(func, return_value=return_value):
            url = query_param_url(context, 'dummy_url')

            assert url == 'http://example.com/dummy?'


class TestSafeDictItems(TestCase):
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


class TestSpacesToUnderscore(TestCase):
    def test_multiple_spaces(self) -> None:
        assert spaces_to_underscore('hello world test') == 'hello_world_test'

    def test_no_spaces(self) -> None:
        assert spaces_to_underscore('hello') == 'hello'

    def test_single_space(self) -> None:
        assert spaces_to_underscore('hello world') == 'hello_world'


class TestToJson(TestCase):
    def test_dict(self) -> None:
        result = to_json({'key': 'value'})
        assert result == '{"key": "value"}'

    def test_invalid_value(self) -> None:
        result = to_json(object())
        assert result == ''

    def test_list(self) -> None:
        result = to_json([1, 2, 3])
        assert result == '[1, 2, 3]'

    def test_nested_structure(self) -> None:
        result = to_json({'list': [1, 2, 3], 'nested': {'key': 'value'}})
        parsed = json.loads(result)

        assert parsed['list'] == [1, 2, 3]
        assert parsed['nested'] == {'key': 'value'}


class TestToSnakeCase(TestCase):
    def test_already_snake_case(self) -> None:
        assert to_snake_case('hello_world') == 'hello_world'

    def test_multiple_spaces(self) -> None:
        assert to_snake_case('Hello World Test') == 'hello_world_test'

    def test_simple_conversion(self) -> None:
        assert to_snake_case('Hello World') == 'hello_world'


class TestUnderscoresToSpaces(TestCase):
    def test_multiple_underscores(self) -> None:
        assert underscores_to_spaces('hello_world_test') == 'hello world test'

    def test_no_underscores(self) -> None:
        assert underscores_to_spaces('hello') == 'hello'

    def test_single_underscore(self) -> None:
        assert underscores_to_spaces('hello_world') == 'hello world'


class TemplateRenderingTests(TestCase):
    def test_render_add_str_filter(self) -> None:
        template_code = """
            {% load spire_core_tags %}

            {{ "Hello" | add_str:" World" }}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert 'Hello World' in rendered

    def test_render_to_snake_case_tag(self) -> None:
        template_code = """
            {% load spire_core_tags %}

            {% to_snake_case "Hello World" as snake_case %}
            {{ snake_case }}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert 'hello_world' in rendered

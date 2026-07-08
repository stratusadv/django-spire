from __future__ import annotations

import unittest

from django.template import Context, Template

from django_spire.core.templatetags.django_spire_string_formatting import (
    dashes_and_spaces_to_underscore,
    dashes_to_underscore,
    spaces_to_underscore,
    underscores_to_spaces,
    to_camel_case,
    to_camel_case_javascript_safe,
    to_snake_case,
)


class TestDashesToUnderscore(unittest.TestCase):
    def test_multiple_dashes(self) -> None:
        assert dashes_to_underscore('hello-world-test') == 'hello_world_test'

    def test_no_dashes(self) -> None:
        assert dashes_to_underscore('hello') == 'hello'

    def test_single_dash(self) -> None:
        assert dashes_to_underscore('hello-world') == 'hello_world'


class TestDashesAndSpacesToUnderscore(unittest.TestCase):
    def test_dashes_and_spaces(self) -> None:
        assert dashes_and_spaces_to_underscore('hello-world test') == 'hello_world_test'

    def test_no_changes_needed(self) -> None:
        assert dashes_and_spaces_to_underscore('hello_world') == 'hello_world'

    def test_only_dashes(self) -> None:
        assert dashes_and_spaces_to_underscore('hello-world') == 'hello_world'

    def test_only_spaces(self) -> None:
        assert dashes_and_spaces_to_underscore('hello world') == 'hello_world'


class TestSpacesToUnderscore(unittest.TestCase):
    def test_multiple_spaces(self) -> None:
        assert spaces_to_underscore('hello world test') == 'hello_world_test'

    def test_no_spaces(self) -> None:
        assert spaces_to_underscore('hello') == 'hello'

    def test_single_space(self) -> None:
        assert spaces_to_underscore('hello world') == 'hello_world'


class TestUnderscoresToSpaces(unittest.TestCase):
    def test_multiple_underscores(self) -> None:
        assert underscores_to_spaces('hello_world_test') == 'hello world test'

    def test_no_underscores(self) -> None:
        assert underscores_to_spaces('hello') == 'hello'

    def test_single_underscore(self) -> None:
        assert underscores_to_spaces('hello_world') == 'hello world'


class TestToSnakeCaseFilter(unittest.TestCase):
    def test_already_snake_case(self) -> None:
        assert to_snake_case('hello_world') == 'hello_world'

    def test_multiple_spaces(self) -> None:
        assert to_snake_case('Hello World Test') == 'hello_world_test'

    def test_simple_conversion(self) -> None:
        assert to_snake_case('Hello World') == 'hello_world'

    def test_camel_case_to_snake(self) -> None:
        assert to_snake_case('helloWorld') == 'hello_world'

    def test_mixed_camel_case(self) -> None:
        assert to_snake_case('myTestCaseFunction') == 'my_test_case_function'

    def test_with_dashes(self) -> None:
        assert to_snake_case('hello-world-test') == 'hello_world_test'

    def test_with_spaces_and_dashes(self) -> None:
        assert to_snake_case('Hello-World Test') == 'hello_world_test'

    def test_empty_string(self) -> None:
        assert to_snake_case('') == ''


class TestToCamelCase(unittest.TestCase):
    def test_simple_words(self) -> None:
        assert to_camel_case('hello world') == 'helloWorld'

    def test_all_caps(self) -> None:
        assert to_camel_case('HELLO WORLD') == 'helloWorld'

    def test_mixed_case_input(self) -> None:
        assert to_camel_case('Hello World Test') == 'helloWorldTest'

    def test_single_word(self) -> None:
        assert to_camel_case('hello') == 'hello'

    def test_with_dashes(self) -> None:
        assert to_camel_case('hello-world-test') == 'helloWorldTest'

    def test_empty_string(self) -> None:
        assert to_camel_case('') == ''

    def test_numeric_input(self) -> None:
        assert to_camel_case('test123') == 'test123'

    def test_camel_case_input_lowercased(self) -> None:
        assert to_camel_case('helloWorld') == 'helloworld'

    def test_snake_case_unchanged(self) -> None:
        assert to_camel_case('hello_world_test') == 'hello_world_test'

    def test_mixed_with_numbers_unchanged(self) -> None:
        assert to_camel_case('userId123') == 'userid123'


class TestToCamelCaseJavascriptSafe(unittest.TestCase):
    def test_simple_conversion(self) -> None:
        assert to_camel_case_javascript_safe('hello world') == 'helloWorld'

    def test_leading_digit_prefixed(self) -> None:
        result = to_camel_case_javascript_safe('123abc')
        assert result == '_123abc'
        assert result[0] == '_'

    def test_starts_with_letter(self) -> None:
        assert to_camel_case_javascript_safe('abc123') == 'abc123'

    def test_empty_string(self) -> None:
        assert to_camel_case_javascript_safe('') == ''

    def test_snake_case_unchanged(self) -> None:
        result = to_camel_case_javascript_safe('hello_world_123')
        assert result == 'hello_world_123'

    def test_camel_case_lowercased(self) -> None:
        result = to_camel_case_javascript_safe('helloWorld')
        assert result == 'helloworld'


class TestStringFormattingTemplateRendering(unittest.TestCase):
    def test_render_to_snake_case_filter(self) -> None:
        template_code = """
            {% load django_spire_string_formatting %}

            {{ value | to_snake_case }}
        """

        tmpl = Template(template_code)
        context = Context({'value': 'Hello World'})
        rendered = tmpl.render(context)
        assert 'hello_world' in rendered

    def test_render_dashes_to_underscore_filter(self) -> None:
        template_code = """
            {% load django_spire_string_formatting %}

            {{ value | dashes_to_underscore }}
        """

        tmpl = Template(template_code)
        context = Context({'value': 'hello-world-test'})
        rendered = tmpl.render(context)
        assert 'hello_world_test' in rendered

    def test_render_underscores_to_spaces_filter(self) -> None:
        template_code = """
            {% load django_spire_string_formatting %}

            {{ value | underscores_to_spaces }}
        """

        tmpl = Template(template_code)
        context = Context({'value': 'hello_world_test'})
        rendered = tmpl.render(context)
        assert 'hello world test' in rendered

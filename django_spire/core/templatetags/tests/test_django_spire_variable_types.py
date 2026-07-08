from __future__ import annotations

import unittest

from django.template import Context, Template

from django_spire.core.templatetags.django_spire_variable_types import (
    is_dict,
    is_list,
    is_list_or_tuple,
    is_not_dict,
    is_not_list,
    is_not_list_or_tuple,
    is_not_tuple,
    is_tuple,
)


class TestIsDict(unittest.TestCase):
    def test_dict(self) -> None:
        assert is_dict({'key': 'value'}) is True

    def test_empty_dict(self) -> None:
        assert is_dict({}) is True

    def test_list(self) -> None:
        assert is_dict([]) is False

    def test_string(self) -> None:
        assert is_dict('string') is False


class TestIsNotDict(unittest.TestCase):
    def test_dict(self) -> None:
        assert is_not_dict({'key': 'value'}) is False

    def test_list(self) -> None:
        assert is_not_dict([]) is True

    def test_string(self) -> None:
        assert is_not_dict('string') is True


class TestIsList(unittest.TestCase):
    def test_dict(self) -> None:
        assert is_list({}) is False

    def test_empty_list(self) -> None:
        assert is_list([]) is True

    def test_list(self) -> None:
        assert is_list([1, 2, 3]) is True

    def test_tuple(self) -> None:
        assert is_list((1, 2, 3)) is False


class TestIsNotList(unittest.TestCase):
    def test_dict(self) -> None:
        assert is_not_list({}) is True

    def test_list(self) -> None:
        assert is_not_list([1, 2, 3]) is False

    def test_tuple(self) -> None:
        assert is_not_list((1, 2, 3)) is True


class TestIsListOrTuple(unittest.TestCase):
    def test_dict(self) -> None:
        assert is_list_or_tuple({}) is False

    def test_list(self) -> None:
        assert is_list_or_tuple([1, 2, 3]) is True

    def test_string(self) -> None:
        assert is_list_or_tuple('string') is False

    def test_tuple(self) -> None:
        assert is_list_or_tuple((1, 2, 3)) is True


class TestIsNotListOrTuple(unittest.TestCase):
    def test_dict(self) -> None:
        assert is_not_list_or_tuple({}) is True

    def test_list(self) -> None:
        assert is_not_list_or_tuple([1, 2, 3]) is False

    def test_string(self) -> None:
        assert is_not_list_or_tuple('string') is True

    def test_tuple(self) -> None:
        assert is_not_list_or_tuple((1, 2, 3)) is False


class TestIsTuple(unittest.TestCase):
    def test_list(self) -> None:
        assert is_tuple([1, 2, 3]) is False

    def test_tuple(self) -> None:
        assert is_tuple((1, 2, 3)) is True

    def test_string(self) -> None:
        assert is_tuple('string') is False

    def test_empty_tuple(self) -> None:
        assert is_tuple(()) is True


class TestIsNotTuple(unittest.TestCase):
    def test_list(self) -> None:
        assert is_not_tuple([1, 2, 3]) is True

    def test_tuple(self) -> None:
        assert is_not_tuple((1, 2, 3)) is False

    def test_string(self) -> None:
        assert is_not_tuple('string') is True


class TestVariableTypesTemplateRendering(unittest.TestCase):
    def test_render_is_dict_filter(self) -> None:
        template_code = """
            {% load django_spire_variable_types %}

            {% if value|is_dict %}value is dict{% else %}value is not dict{% endif %}
        """

        tmpl = Template(template_code)
        context = Context({'value': {'key': 'val'}})
        rendered = tmpl.render(context)
        assert 'value is dict' in rendered

    def test_render_is_list_filter(self) -> None:
        template_code = """
            {% load django_spire_variable_types %}

            {% if value|is_list %}value is list{% else %}value is not list{% endif %}
        """

        tmpl = Template(template_code)
        context = Context({'value': [1, 2, 3]})
        rendered = tmpl.render(context)
        assert 'value is list' in rendered

    def test_render_is_tuple_filter(self) -> None:
        template_code = """
            {% load django_spire_variable_types %}

            {% if value|is_tuple %}value is tuple{% else %}value is not tuple{% endif %}
        """

        tmpl = Template(template_code)
        context = Context({'value': (1, 2, 3)})
        rendered = tmpl.render(context)
        assert 'value is tuple' in rendered

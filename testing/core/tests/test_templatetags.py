from __future__ import annotations

import string

from unittest.mock import patch

from django.template import Context, RequestContext, Template
from django.test import RequestFactory, TestCase

from django_spire.core.templatetags.core_tags import (
    add_str,
    content_type_url,
    in_list,
    index,
    generate_id,
    not_in_list,
    query_param_url,
    to_snake_case,
)


class TemplateTagUnitTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_add_str(self) -> None:
        self.assertEqual(add_str('Hello', 'World'), 'HelloWorld')

    def test_in_list(self) -> None:
        self.assertTrue(in_list('a', 'a,b,c'))
        self.assertFalse(in_list('d', 'a,b,c'))

    def test_index(self) -> None:
        items = [10, 20, 30]

        self.assertEqual(index(items, 1), 20)
        self.assertEqual(index(items, 5), items)

    def test_generate_id(self) -> None:
        identifier = generate_id()

        self.assertEqual(len(identifier), 8)
        self.assertTrue(all(ch in string.ascii_letters for ch in identifier))

    def test_not_in_list(self) -> None:
        self.assertTrue(not_in_list('x', 'a,b,c'))
        self.assertFalse(not_in_list('a', 'a,b,c'))

    def test_to_snake_case(self) -> None:
        self.assertEqual(to_snake_case('Hello World'), 'hello_world')

    def test_content_type_url(self) -> None:
        class Dummy:
            pass

        dummy = Dummy()

        dummy._meta = type(
            'meta',
            (),
            {'app_label': 'myapp', 'model_name': 'dummy'}
        )

        func = 'django_spire.core.templatetags.core_tags.reverse'
        return_value = 'http://example.com/dummy'

        with patch(func, return_value=return_value) as mock_reverse:
            url = content_type_url('dummy_url', dummy)

            mock_reverse.assert_called_once_with(
                'dummy_url',
                kwargs={'app_label': 'myapp', 'model_name': 'dummy'}
            )

            self.assertEqual(url, 'http://example.com/dummy')

    def test_query_param_url(self) -> None:
        request = self.factory.get('/some_path', {'foo': 'bar', 'baz': 'qux'})
        context = RequestContext(request, {})

        func = 'django_spire.core.templatetags.core_tags.reverse'
        return_value = 'http://example.com/dummy'

        with patch(func, return_value=return_value) as mock_reverse:
            url = query_param_url(context, 'dummy_url')
            mock_reverse.assert_called_once_with('dummy_url', kwargs={})

            self.assertTrue(url.startswith('http://example.com/dummy?'))
            self.assertIn('foo=bar', url)
            self.assertIn('baz=qux', url)


class TemplateRenderingTests(TestCase):
    def test_render_add_str_filter(self) -> None:
        template_code = """
            {% load spire_core_tags %}

            {{ "Hello" | add_str:" World" }}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        self.assertIn('Hello World', rendered)

    def test_render_to_snake_case_tag(self) -> None:
        template_code = """
            {% load spire_core_tags %}

            {% to_snake_case "Hello World" as snake_case %}
            {{ snake_case }}
        """

        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        self.assertIn('hello_world', rendered)

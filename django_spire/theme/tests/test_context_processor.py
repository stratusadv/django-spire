from __future__ import annotations

from unittest.mock import patch
from typing_extensions import Any

from django.test import TestCase, RequestFactory

from django_spire.core.context_processors import theme_context
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.theme.utils import get_theme_cookie_name


class ThemeContextProcessorTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_theme_context_no_cookie(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}

        with patch('django_spire.conf.settings.DJANGO_SPIRE_DEFAULT_THEME', 'dracula-dark'):
            context = theme_context(request)

        self.assertEqual(context['DJANGO_SPIRE_DEFAULT_THEME'], 'dracula-dark')
        self.assertIn('theme', context)

        data = context['theme']
        self.assertEqual(data['family'], 'dracula')
        self.assertEqual(data['mode'], 'dark')

    def test_theme_context_with_cookie(self) -> None:
        request = self.factory.get('/')
        cookie_name = get_theme_cookie_name()
        request.COOKIES = {cookie_name: 'one-dark-light'}

        context = theme_context(request)

        self.assertIn('theme', context)
        data = context['theme']
        self.assertEqual(data['family'], 'one-dark')
        self.assertEqual(data['mode'], 'light')

    def test_theme_context_invalid_cookie(self) -> None:
        request = self.factory.get('/')
        cookie_name = get_theme_cookie_name()
        request.COOKIES = {cookie_name: 'invalid-theme'}

        with patch('django_spire.conf.settings.DJANGO_SPIRE_DEFAULT_THEME', 'dracula-dark'):
            context = theme_context(request)

        data = context['theme']
        self.assertEqual(data['family'], 'dracula')
        self.assertEqual(data['mode'], 'dark')

    def test_theme_context_path_setting(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}

        path = '/custom/path/{family}/{mode}.css'
        with patch('django_spire.conf.settings.DJANGO_SPIRE_THEME_PATH', path):
            context = theme_context(request)

        self.assertEqual(context['DJANGO_SPIRE_THEME_PATH'], path)


class ThemeContextProcessorIntegrationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()

    def test_theme_context_with_authenticated_client(self) -> None:
        cookie_name = get_theme_cookie_name()
        self.client.cookies[cookie_name] = 'dracula-dark'
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_theme_context_with_media_root_override(self) -> None:
        request = self.factory.get('/')
        cookie_name = get_theme_cookie_name()
        request.COOKIES = {cookie_name: 'material-light'}

        context = theme_context(request)
        data = context['theme']
        self.assertEqual(data['family'], 'material')
        self.assertEqual(data['mode'], 'light')

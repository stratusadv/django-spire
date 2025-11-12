from __future__ import annotations

import json

from http import HTTPStatus
from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.theme.enums import ThemeFamily
from django_spire.theme.utils import get_theme_cookie_name
from django_spire.theme.views import json_views


class ThemeViewTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_get_config_success(self) -> None:
        request = self.factory.get('/django_spire/theme/json/get_config/')
        response = json_views.get_config(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.content)
        self.assertTrue(data['success'])

        config = data['data']
        self.assertIn('families', config)
        self.assertIn('default_family', config)
        self.assertIn('default_mode', config)
        self.assertIn('separator', config)

        for family in ThemeFamily:
            self.assertIn(family.value, config['families'])
            family_config = config['families'][family.value]
            self.assertIn('name', family_config)
            self.assertIn('modes', family_config)
            self.assertEqual(set(family_config['modes']), {'dark', 'light'})

    def test_get_config_cache_header(self) -> None:
        _ = self.factory.get('/django_spire/theme/json/get_config/')

        with patch('django_spire.theme.views.json_views.cache_page') as _:
            self.assertTrue(hasattr(json_views.get_config, '__wrapped__'))

    def test_set_theme_success(self) -> None:
        request = self.factory.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({'theme': 'gruvbox-dark'}),
            content_type='application/json'
        )
        response = json_views.set_theme(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('theme', data)

        data = data['theme']
        self.assertEqual(data['family'], 'gruvbox')
        self.assertEqual(data['mode'], 'dark')

        cookie_name = get_theme_cookie_name()
        self.assertIn(cookie_name, response.cookies)
        self.assertEqual(response.cookies[cookie_name].value, 'gruvbox-dark')

    def test_set_theme_missing_theme(self) -> None:
        request = self.factory.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({}),
            content_type='application/json'
        )
        response = json_views.set_theme(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Theme is required')

    def test_set_theme_invalid_theme(self) -> None:
        request = self.factory.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({'theme': 'invalid-theme'}),
            content_type='application/json'
        )
        response = json_views.set_theme(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertIn('Invalid theme', data['error'])


class ThemeViewIntegrationTests(BaseTestCase):
    def test_set_theme_with_authenticated_client(self) -> None:
        response = self.client.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({'theme': 'gruvbox-dark'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_get_config_with_authenticated_client(self) -> None:
        response = self.client.get('/django_spire/theme/json/get_config/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('families', data['data'])

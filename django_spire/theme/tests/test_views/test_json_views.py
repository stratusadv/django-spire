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

        assert isinstance(response, JsonResponse)
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content)
        assert data['success']

        config = data['data']
        assert 'families' in config
        assert 'default_family' in config
        assert 'default_mode' in config
        assert 'separator' in config

        for family in ThemeFamily:
            assert family.value in config['families']
            family_config = config['families'][family.value]
            assert 'name' in family_config
            assert 'modes' in family_config
            assert set(family_config['modes']) == {'dark', 'light'}

    def test_get_config_cache_header(self) -> None:
        _ = self.factory.get('/django_spire/theme/json/get_config/')

        with patch('django_spire.theme.views.json_views.cache_page') as _:
            assert hasattr(json_views.get_config, '__wrapped__')

    def test_set_theme_success(self) -> None:
        request = self.factory.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({'theme': 'gruvbox-dark'}),
            content_type='application/json'
        )
        response = json_views.set_theme(request)

        assert isinstance(response, JsonResponse)
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content)
        assert data['success']
        assert 'theme' in data

        data = data['theme']
        assert data['family'] == 'gruvbox'
        assert data['mode'] == 'dark'

        cookie_name = get_theme_cookie_name()
        assert cookie_name in response.cookies
        assert response.cookies[cookie_name].value == 'gruvbox-dark'

    def test_set_theme_missing_theme(self) -> None:
        request = self.factory.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({}),
            content_type='application/json'
        )
        response = json_views.set_theme(request)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.content)
        assert not data['success']
        assert 'error' in data
        assert data['error'] == 'Theme is required'

    def test_set_theme_invalid_theme(self) -> None:
        request = self.factory.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({'theme': 'invalid-theme'}),
            content_type='application/json'
        )
        response = json_views.set_theme(request)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.content)
        assert not data['success']
        assert 'error' in data
        assert 'Invalid theme' in data['error']


class ThemeViewIntegrationTests(BaseTestCase):
    def test_set_theme_with_authenticated_client(self) -> None:
        response = self.client.post(
            '/django_spire/theme/json/set_theme/',
            data=json.dumps({'theme': 'gruvbox-dark'}),
            content_type='application/json'
        )

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert data['success']

    def test_get_config_with_authenticated_client(self) -> None:
        response = self.client.get('/django_spire/theme/json/get_config/')
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content)
        assert data['success']
        assert 'families' in data['data']

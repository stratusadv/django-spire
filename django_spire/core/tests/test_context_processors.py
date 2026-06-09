from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase, override_settings

from django_spire.core.context_processors import django_spire, theme_context


class TestDjangoSpireContextProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    @override_settings(DJANGO_SPIRE_AUTH_CONTROLLERS=[])
    def test_empty_auth_controllers(self) -> None:
        request = self.factory.get('/')
        result = django_spire(request)

        assert 'DJANGO_SPIRE_VERSION' in result
        assert 'AuthController' in result
        assert result['AuthController'] == {}

    @override_settings(DJANGO_SPIRE_AUTH_CONTROLLERS=['test_app'])
    @patch('django_spire.core.context_processors.AppAuthController')
    def test_with_auth_controllers(self, mock_controller: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_controller.return_value = mock_instance

        request = self.factory.get('/')
        result = django_spire(request)

        assert 'AuthController' in result
        assert 'test_app' in result['AuthController']
        mock_controller.assert_called_once_with('test_app', request=request)


class TestThemeContextProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_default_theme_light(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}
        result = theme_context(request)

        assert result['DJANGO_SPIRE_THEME_MODE'] == 'light'
        assert result['DJANGO_SPIRE_THEME_COOKIE_NAME'] == 'django_spire-theme-mode'

    def test_theme_from_cookie_dark(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {'django_spire-theme-mode': 'dark'}
        result = theme_context(request)

        assert result['DJANGO_SPIRE_THEME_MODE'] == 'dark'

    @override_settings(DJANGO_SPIRE_DEFAULT_THEME_MODE='dark')
    def test_custom_default_theme_mode(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}
        result = theme_context(request)

        assert result['DJANGO_SPIRE_THEME_MODE'] == 'dark'

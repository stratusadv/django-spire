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

    def test_default_theme_applied(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}
        result = theme_context(request)

        assert 'DJANGO_SPIRE_DEFAULT_THEME' in result
        assert 'DJANGO_SPIRE_THEME_COOKIE_NAME' in result
        assert 'DJANGO_SPIRE_THEME_PATH' in result
        assert 'theme' in result

    @override_settings(DJANGO_SPIRE_DEFAULT_THEME='default-dark')
    def test_custom_default_theme(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}
        result = theme_context(request)

        assert result['DJANGO_SPIRE_DEFAULT_THEME'] == 'default-dark'

    @override_settings(DJANGO_SPIRE_THEME_PATH='/custom/path/{family}/app-{mode}.css')
    def test_custom_theme_path(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}
        result = theme_context(request)

        assert result['DJANGO_SPIRE_THEME_PATH'] == '/custom/path/{family}/app-{mode}.css'

    @patch('django_spire.core.context_processors.get_theme_cookie_name')
    @patch('django_spire.core.context_processors.Theme')
    def test_theme_from_cookie(self, mock_theme: MagicMock, mock_cookie_name: MagicMock) -> None:
        mock_cookie_name.return_value = 'theme_cookie'
        mock_theme_instance = MagicMock()
        mock_theme_instance.value = 'custom-dark'
        mock_theme_instance.to_dict.return_value = {'family': 'custom', 'mode': 'dark'}
        mock_theme.from_string.return_value = mock_theme_instance
        mock_theme.get_default.return_value = mock_theme_instance

        request = self.factory.get('/')
        request.COOKIES = {'theme_cookie': 'custom-dark'}
        result = theme_context(request)

        assert result['theme'] == {'family': 'custom', 'mode': 'dark'}

    def test_theme_result_contains_required_keys(self) -> None:
        request = self.factory.get('/')
        request.COOKIES = {}
        result = theme_context(request)

        assert 'theme' in result
        assert isinstance(result['theme'], dict)

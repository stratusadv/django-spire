from __future__ import annotations

from django.test import RequestFactory, TestCase, override_settings

from django_spire.core.context_processors import django_spire, theme_context


class TestDjangoSpireContextProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_returns_version(self) -> None:
        request = self.factory.get('/')
        result = django_spire(request)

        assert 'DJANGO_SPIRE_VERSION' in result


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

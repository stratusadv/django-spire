from __future__ import annotations

from django.test import TestCase, override_settings

from django_spire.conf import Settings, settings


class TestSettings(TestCase):
    def test_getattr_returns_django_setting(self) -> None:
        assert settings.DEBUG is not None

    def test_getattr_returns_django_spire_default(self) -> None:
        result = settings.DJANGO_SPIRE_DEFAULT_THEME

        assert result == 'default-light'

    def test_getattr_returns_none_for_unknown_setting(self) -> None:
        result = settings.NONEXISTENT_SETTING_NAME

        assert result is None

    @override_settings(DJANGO_SPIRE_DEFAULT_THEME='custom-dark')
    def test_django_setting_overrides_default(self) -> None:
        fresh_settings = Settings()

        result = fresh_settings.DJANGO_SPIRE_DEFAULT_THEME

        assert result == 'custom-dark'

    @override_settings(
        DJANGO_SPIRE_AUTH_CONTROLLERS={'custom_app': 'custom.path.Controller'}
    )
    def test_auth_controllers_merges_dicts(self) -> None:
        fresh_settings = Settings()

        result = fresh_settings.DJANGO_SPIRE_AUTH_CONTROLLERS

        assert 'custom_app' in result
        assert 'ai_chat' in result

    def test_settings_instance_exists(self) -> None:
        assert settings is not None
        assert isinstance(settings, Settings)

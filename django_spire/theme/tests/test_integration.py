from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.theme.enums import ThemeFamily
from django_spire.theme.models import Theme


class ThemeIntegrationTests(BaseTestCase):
    def test_all_themes_have_stylesheets(self) -> None:
        for theme in Theme.get_available():
            stylesheet = theme.stylesheet

            assert f'{theme.family.value}/' in stylesheet
            assert f'app-{theme.mode.value}.css' in stylesheet

    def test_roundtrip_conversion(self) -> None:
        for theme in Theme.get_available():
            string = theme.value
            recovered = Theme.from_string(string)
            assert theme == recovered

            dictionary = theme.to_dict()
            recovered2 = Theme.from_string(dictionary['full'])
            assert theme == recovered2

    def test_display_names_complete(self) -> None:
        for family in ThemeFamily:
            assert family in Theme.FAMILY_DISPLAY_NAMES
            display_name = Theme.FAMILY_DISPLAY_NAMES[family]
            assert isinstance(display_name, str)
            assert len(display_name) > 0

    def test_theme_integration_with_authenticated_user(self) -> None:
        available = Theme.get_available()
        assert len(available) > 0

        for theme in available[:3]:
            self.client.cookies['app-theme'] = theme.value
            response = self.client.get('/')
            assert response.status_code == 200

    def test_theme_media_integration(self) -> None:
        theme = Theme(family=ThemeFamily.GRUVBOX, mode='dark')
        stylesheet = theme.stylesheet

        assert 'django_spire/css/themes/' in stylesheet
        assert 'gruvbox' in stylesheet
        assert 'app-dark.css' in stylesheet

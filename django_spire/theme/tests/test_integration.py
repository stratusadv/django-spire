from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.theme.enums import ThemeFamily
from django_spire.theme.models import Theme


class ThemeIntegrationTests(BaseTestCase):
    def test_all_themes_have_stylesheets(self) -> None:
        for theme in Theme.get_available():
            stylesheet = theme.stylesheet

            self.assertIn(f'{theme.family.value}/', stylesheet)
            self.assertIn(f'app-{theme.mode.value}.css', stylesheet)

    def test_roundtrip_conversion(self) -> None:
        for theme in Theme.get_available():
            string = theme.value
            recovered = Theme.from_string(string)
            self.assertEqual(theme, recovered)

            dictionary = theme.to_dict()
            recovered2 = Theme.from_string(dictionary['full'])
            self.assertEqual(theme, recovered2)

    def test_display_names_complete(self) -> None:
        for family in ThemeFamily:
            self.assertIn(family, Theme.FAMILY_DISPLAY_NAMES)
            display_name = Theme.FAMILY_DISPLAY_NAMES[family]
            self.assertIsInstance(display_name, str)
            self.assertTrue(len(display_name) > 0)

    def test_theme_integration_with_authenticated_user(self) -> None:
        available = Theme.get_available()
        self.assertGreater(len(available), 0)

        for theme in available[:3]:
            self.client.cookies['app-theme'] = theme.value
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

    def test_theme_media_integration(self) -> None:
        theme = Theme(family=ThemeFamily.DRACULA, mode='dark')
        stylesheet = theme.stylesheet

        self.assertIn('django_spire/css/themes/', stylesheet)
        self.assertIn('dracula', stylesheet)
        self.assertIn('app-dark.css', stylesheet)

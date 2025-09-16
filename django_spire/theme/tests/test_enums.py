from __future__ import annotations

from django.test import TestCase

from django_spire.theme.enums import ThemeFamily, ThemeMode


class ThemeEnumTests(TestCase):
    def test_theme_families_match_filesystem(self) -> None:
        expected = {
            'ayu',
            'catppuccin',
            'default',
            'dracula',
            'gruvbox',
            'material',
            'nord',
            'oceanic-next',
            'one-dark',
            'palenight',
            'rose-pine',
            'synthwave',
            'tokyo-night'
        }

        actual = {family.value for family in ThemeFamily}
        self.assertEqual(actual, expected)

    def test_theme_modes(self) -> None:
        expected = {'dark', 'light'}
        actual = {mode.value for mode in ThemeMode}
        self.assertEqual(actual, expected)

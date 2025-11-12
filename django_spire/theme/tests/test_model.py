from __future__ import annotations

import pytest

from dataclasses import fields

from django.test import TestCase

from django_spire.theme.enums import ThemeFamily, ThemeMode
from django_spire.theme.models import Theme


class ThemeModelTests(TestCase):
    def test_dataclass_fields(self) -> None:
        theme_fields = {f.name: f.type for f in fields(Theme)}

        self.assertEqual(set(theme_fields.keys()), {'family', 'mode'})
        self.assertEqual(theme_fields['family'], 'ThemeFamily')
        self.assertEqual(theme_fields['mode'], 'ThemeMode')

    def test_class_variables(self) -> None:
        self.assertEqual(Theme.DEFAULT_FAMILY, ThemeFamily.DEFAULT)
        self.assertEqual(Theme.DEFAULT_MODE, ThemeMode.LIGHT)
        self.assertEqual(Theme.SEPARATOR, '-')

        for family in ThemeFamily:
            self.assertIn(family, Theme.FAMILY_DISPLAY_NAMES)

    def test_theme_initialization_with_enums(self) -> None:
        theme = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.DARK)
        self.assertEqual(theme.family, ThemeFamily.GRUVBOX)
        self.assertEqual(theme.mode, ThemeMode.DARK)

    def test_theme_initialization_with_strings(self) -> None:
        theme = Theme(family='gruvbox', mode='dark')
        self.assertEqual(theme.family, ThemeFamily.GRUVBOX)
        self.assertEqual(theme.mode, ThemeMode.DARK)

    def test_theme_initialization_invalid_family(self) -> None:
        with pytest.raises(ValueError) as ctx:
            Theme(family='invalid-family', mode='dark')
        self.assertIn('Invalid theme family', str(ctx.value))

    def test_theme_initialization_invalid_mode(self) -> None:
        with pytest.raises(ValueError) as ctx:
            Theme(family='gruvbox', mode='invalid-mode')
        self.assertIn('Invalid theme mode', str(ctx.value))

    def test_from_string_valid(self) -> None:
        cases = [
            ('default-light', ThemeFamily.DEFAULT, ThemeMode.LIGHT),
            ('gruvbox-dark', ThemeFamily.GRUVBOX, ThemeMode.DARK),
            ('one-dark-light', ThemeFamily.ONE_DARK, ThemeMode.LIGHT),
            ('tokyo-night-dark', ThemeFamily.TOKYO_NIGHT, ThemeMode.DARK),
        ]

        for string, family, mode in cases:
            with self.subTest(string=string):
                theme = Theme.from_string(string)
                self.assertEqual(theme.family, family)
                self.assertEqual(theme.mode, mode)

    def test_from_string_empty_with_default(self) -> None:
        default = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.DARK)
        theme = Theme.from_string('', default=default)
        self.assertEqual(theme, default)

    def test_from_string_empty_without_default(self) -> None:
        theme = Theme.from_string('')
        self.assertEqual(theme.family, Theme.DEFAULT_FAMILY)
        self.assertEqual(theme.mode, Theme.DEFAULT_MODE)

    def test_from_string_invalid_with_default(self) -> None:
        default = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.DARK)
        theme = Theme.from_string('invalid', default=default)
        self.assertEqual(theme, default)

    def test_from_string_invalid_without_default(self) -> None:
        with pytest.raises(ValueError):
            Theme.from_string('invalid')

    def test_get_available(self) -> None:
        available = Theme.get_available()

        count = len(ThemeFamily) * len(ThemeMode)
        self.assertEqual(len(available), count)

        for family in ThemeFamily:
            for mode in ThemeMode:
                theme = Theme(family=family, mode=mode)
                self.assertIn(theme, available)

    def test_get_default(self) -> None:
        default = Theme.get_default()
        self.assertEqual(default.family, Theme.DEFAULT_FAMILY)
        self.assertEqual(default.mode, Theme.DEFAULT_MODE)

    def test_display_property(self) -> None:
        theme = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.DARK)
        self.assertEqual(theme.display, 'Gruvbox - Dark')

        theme = Theme(family=ThemeFamily.ONE_DARK, mode=ThemeMode.LIGHT)
        self.assertEqual(theme.display, 'One Dark Pro - Light')

    def test_family_display_property(self) -> None:
        theme = Theme(family=ThemeFamily.ONE_DARK, mode=ThemeMode.DARK)
        self.assertEqual(theme.family_display, 'One Dark Pro')

    def test_is_dark_property(self) -> None:
        dark = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.DARK)
        self.assertTrue(dark.is_dark)

        light = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.LIGHT)
        self.assertFalse(light.is_dark)

    def test_stylesheet_property(self) -> None:
        cases = [
            (ThemeFamily.DEFAULT, ThemeMode.LIGHT, 'django_spire/css/themes/default/app-light.css'),
            (ThemeFamily.GRUVBOX, ThemeMode.DARK, 'django_spire/css/themes/gruvbox/app-dark.css'),
            (ThemeFamily.ONE_DARK, ThemeMode.LIGHT, 'django_spire/css/themes/one-dark/app-light.css'),
            (ThemeFamily.TOKYO_NIGHT, ThemeMode.DARK, 'django_spire/css/themes/tokyo-night/app-dark.css'),
        ]

        for family, mode, path in cases:
            with self.subTest(family=family, mode=mode):
                theme = Theme(family=family, mode=mode)
                self.assertEqual(theme.stylesheet, path)

    def test_value_property(self) -> None:
        cases = [
            (ThemeFamily.DEFAULT, ThemeMode.LIGHT, 'default-light'),
            (ThemeFamily.GRUVBOX, ThemeMode.DARK, 'gruvbox-dark'),
            (ThemeFamily.ONE_DARK, ThemeMode.LIGHT, 'one-dark-light'),
            (ThemeFamily.TOKYO_NIGHT, ThemeMode.DARK, 'tokyo-night-dark'),
        ]

        for family, mode, value in cases:
            with self.subTest(family=family, mode=mode):
                theme = Theme(family=family, mode=mode)
                self.assertEqual(theme.value, value)

    def test_to_dict(self) -> None:
        theme = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.DARK)
        result = theme.to_dict()

        keys = {
            'display',
            'family',
            'family_display',
            'full',
            'is_dark',
            'mode',
            'stylesheet'
        }

        self.assertEqual(set(result.keys()), keys)

        self.assertEqual(result['display'], 'Gruvbox - Dark')
        self.assertEqual(result['family'], 'gruvbox')
        self.assertEqual(result['family_display'], 'Gruvbox')
        self.assertEqual(result['full'], 'gruvbox-dark')
        self.assertTrue(result['is_dark'])
        self.assertEqual(result['mode'], 'dark')
        self.assertEqual(result['stylesheet'], 'django_spire/css/themes/gruvbox/app-dark.css')

    def test_theme_immutability(self) -> None:
        theme = Theme(family=ThemeFamily.GRUVBOX, mode=ThemeMode.DARK)

        with pytest.raises(AttributeError):
            theme.family = ThemeFamily.DEFAULT

        with pytest.raises(AttributeError):
            theme.mode = ThemeMode.LIGHT

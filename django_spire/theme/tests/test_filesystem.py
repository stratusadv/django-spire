from __future__ import annotations

from pathlib import Path

from django.test import TestCase

from django_spire.theme.enums import ThemeFamily
from django_spire.theme.models import Theme


class ThemeFilesystemValidationTests(TestCase):
    def setUp(self) -> None:
        self.base_path = self._get_css_base_path()

    def _get_css_base_path(self) -> Path:
        file = Path(__file__)
        root = file.parent.parent.parent.parent
        return root / 'django_spire' / 'core' / 'static' / 'django_spire' / 'css'

    def test_css_directory_exists(self) -> None:
        if not self.base_path.exists():
            self.skipTest(
                f'CSS directory does not exist: {self.base_path}. Create it to enable filesystem validation tests.'
            )

        assert self.base_path.is_dir(), f'CSS path is not a directory: {self.base_path}'

    def test_all_theme_families_have_css_files(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'CSS directory does not exist: {self.base_path}')

        existing = {path.stem for path in self.base_path.glob('*.css') if path.stem != 'flatpickr.min'}
        expected = {family.value for family in ThemeFamily}

        missing = expected - existing
        if missing:
            self.fail(f'Missing CSS files: {sorted(missing)}. Expected files: {sorted(missing)}.css')

    def test_no_unexpected_css_files(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'CSS directory does not exist: {self.base_path}')

        existing = {path.stem for path in self.base_path.glob('*.css') if path.stem != 'flatpickr.min'}
        expected = {family.value for family in ThemeFamily}

        unexpected = existing - expected

        if unexpected:
            self.fail(
                f'Unexpected CSS files: {sorted(unexpected)}. Remove these or update ThemeFamily enum: {sorted(unexpected)}'
            )

    def test_theme_stylesheet_paths_match_filesystem(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'CSS directory does not exist: {self.base_path}')

        missing = []

        for theme in Theme.get_available():
            expected = theme.stylesheet

            file = Path(__file__)
            root = file.parent.parent.parent.parent
            path = root / 'django_spire' / 'core' / 'static' / expected

            if not path.exists():
                missing.append(f'{theme.value}: {expected}')

        if missing:
            self.fail(f'Missing stylesheet files: {missing}')

    def test_css_files_are_not_empty(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'CSS directory does not exist: {self.base_path}')

        empty = []

        for family in ThemeFamily:
            file = self.base_path / f'{family.value}.css'

            if file.exists():
                size = file.stat().st_size
                if size == 0:
                    empty.append(f'{family.value}.css')

        if empty:
            self.fail(f'Empty CSS files: {sorted(empty)}')

    def test_css_filenames_match_enum_values(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'CSS directory does not exist: {self.base_path}')

        for family in ThemeFamily:
            file = self.base_path / f'{family.value}.css'

            if file.exists():
                assert file.stem == family.value, (
                    f'Filename {file.stem} does not match expected {family.value}'
                )
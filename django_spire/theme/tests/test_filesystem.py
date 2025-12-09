from __future__ import annotations

from pathlib import Path

from django.test import TestCase

from django_spire.theme.enums import ThemeFamily, ThemeMode
from django_spire.theme.models import Theme


class ThemeFilesystemValidationTests(TestCase):
    def setUp(self) -> None:
        self.base_path = self._get_themes_base_path()

    def _get_themes_base_path(self) -> Path:
        file = Path(__file__)
        root = file.parent.parent.parent.parent
        return root / 'django_spire' / 'core' / 'static' / 'django_spire' / 'css' / 'themes'

    def test_themes_directory_exists(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}. Create it to enable filesystem validation tests.')

        assert self.base_path.is_dir(), f'Themes path is not a directory: {self.base_path}'

    def test_all_theme_families_have_directories(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        existing = {path.name for path in self.base_path.iterdir() if path.is_dir()}
        expected = {family.value for family in ThemeFamily}

        missing = expected - existing
        if missing:
            self.fail(f'Missing theme directories: {sorted(missing)}. Create these directories: {sorted(missing)}')

    def test_no_unexpected_theme_directories(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        existing = {path.name for path in self.base_path.iterdir() if path.is_dir()}
        expected = {family.value for family in ThemeFamily}

        unexpected = existing - expected

        if unexpected:
            self.fail(f'Unexpected theme directories: {sorted(unexpected)}. Remove these or update ThemeFamily enum: {sorted(unexpected)}')

    def test_all_theme_mode_files_exist(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        missing = []

        for family in ThemeFamily:
            directory = self.base_path / family.value

            if not directory.exists():
                missing.extend([f'{family.value}/app-{mode.value}.css' for mode in ThemeMode])
                continue

            for mode in ThemeMode:
                file = directory / f'app-{mode.value}.css'
                if not file.exists():
                    missing.append(f'{family.value}/app-{mode.value}.css')

        if missing:
            self.fail(f'Missing CSS files: {sorted(missing)}')

    def test_no_unexpected_css_files(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        expected = {f'app-{mode.value}.css' for mode in ThemeMode}
        unexpected = {}

        for family in ThemeFamily:
            directory = self.base_path / family.value

            if directory.exists():
                existing = {f.name for f in directory.iterdir() if f.is_file() and f.suffix == '.css'}
                files = existing - expected

                if files:
                    unexpected[family.value] = sorted(files)

        if unexpected:
            self.fail(f'Unexpected CSS files by family: {unexpected}')

    def test_theme_stylesheet_paths_match_filesystem(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

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
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        empty = []

        for family in ThemeFamily:
            directory = self.base_path / family.value

            if directory.exists():
                for mode in ThemeMode:
                    file = directory / f'app-{mode.value}.css'

                    if file.exists():
                        size = file.stat().st_size
                        if size == 0:
                            empty.append(f'{family.value}/app-{mode.value}.css')

        if empty:
            self.fail(f'Empty CSS files: {sorted(empty)}')

    def test_filesystem_structure_completeness(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        total_expected_families = len(ThemeFamily)
        total_expected_modes = len(ThemeMode)
        total_expected_files = total_expected_families * total_expected_modes

        actual = 0

        for family in ThemeFamily:
            directory = self.base_path / family.value

            if directory.exists():
                files = list(directory.glob('app-*.css'))
                actual += len(files)

        if actual != total_expected_files:
            self.fail(f'Expected {total_expected_files} CSS files, found {actual}')

    def test_directory_structure_matches_enum_values(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        missing = []

        for family in ThemeFamily:
            directory = self.base_path / family.value

            if not directory.exists():
                missing.append(family.value)

        if missing:
            self.fail(f'Missing directories for theme families: {sorted(missing)}')

    def test_css_filenames_match_enum_values(self) -> None:
        if not self.base_path.exists():
            self.skipTest(f'Themes directory does not exist: {self.base_path}')

        for family in ThemeFamily:
            directory = self.base_path / family.value

            if directory.exists():
                for mode in ThemeMode:
                    filename = f'app-{mode.value}.css'
                    file = directory / filename

                    if file.exists():
                        assert file.name == filename, f'Filename {file.name} does not match expected {filename}'

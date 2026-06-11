from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import sass
from django.conf import settings
from django.core.management.base import BaseCommand
from importlib.util import find_spec

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    help = 'Compile SCSS to CSS using the bundled theme entry point.'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--output',
            type=Path,
            default=None,
            help='Output directory for compiled CSS. Defaults to STATIC_ROOT/css.',
        )

    def handle(self, **options) -> None:
        output_dir = options['output']
        if output_dir is None:
            output_dir = self._get_static_files_dir() / 'django_spire' / 'css'

        django_spire_scss_source_path = self._get_django_spire_scss_source_path()
        bundled_entry_file = django_spire_scss_source_path / '_theme.scss'

        external_scss_source_path = self._get_static_files_dir()
        external_entry_file = external_scss_source_path / 'django_spire' / 'scss' / '_theme.scss'

        if not external_entry_file.exists():
            external_scss_dir = external_scss_source_path / 'scss'
            external_scss_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f'No external theme found. Creating {external_entry_file}.')
            shutil.copy2(bundled_entry_file, external_entry_file)

        entry_file = external_entry_file
        include_paths = [str(external_scss_source_path), str(django_spire_scss_source_path)]
        self.stdout.write('Using external theme entry file.')

        self.stdout.write(f'Compiling SCSS from: {entry_file}')
        self.stdout.write(f'Output directory: {output_dir}')

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            css_content = sass.compile(
                filename=str(entry_file), output_style='expanded', include_paths=include_paths
            )
        except sass.CompileError as exc:
            self.stderr.write(f'Sass compilation error: {exc}')
            return

        output_file = output_dir / 'django-spire-bootstrap.css'
        output_file.write_bytes(css_content.encode('utf-8'))

        self.stdout.write(self.style.SUCCESS(f'Compiled successfully: {output_file}'))

    @staticmethod
    def _get_django_spire_scss_source_path() -> Path:
        spec = find_spec('django_spire.core')
        if spec and spec.submodule_search_locations:
            core_dir = Path(spec.submodule_search_locations[0])
            candidate = core_dir / 'static' / 'django_spire' / 'scss'
            if candidate.exists():
                return candidate

        for parent in Path(__file__).resolve().parents:
            candidate = parent / 'static' / 'django_spire' / 'scss'
            if candidate.exists():
                return candidate

        message = (
            'Could not locate django-spire SCSS source directory. '
            'Please ensure django-spire is properly installed.'
        )
        raise FileNotFoundError(message)

    @staticmethod
    def _get_static_files_dir() -> Path:
        staticfiles_dir = getattr(settings, 'STATICFILES_DIRS', [])
        if staticfiles_dir:
            first_dir = staticfiles_dir[0]
            if isinstance(first_dir, (str, Path)):
                return Path(first_dir)

        message = 'Could not locate static files directory.'
        raise ValueError(message)

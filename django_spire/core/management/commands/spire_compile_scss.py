from __future__ import annotations

from pathlib import Path

import sass
from django.conf import settings
from django.core.management.base import BaseCommand
from typing import TYPE_CHECKING

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
            output_dir = self._get_default_output_dir()

        django_spire_scss_source_path = self._get_django_spire_scss_source_path()
        bundled_entry_file = django_spire_scss_source_path / '_theme.scss'

        external_scss_source_path = self._get_external_scss_source_path()
        external_entry_file = external_scss_source_path / '_theme.scss'

        if external_entry_file.exists():
            entry_file = external_entry_file
            include_paths = [str(external_scss_source_path), str(django_spire_scss_source_path)]
            self.stdout.write('Using external theme entry file.')
        else:
            entry_file = bundled_entry_file
            include_paths = [str(django_spire_scss_source_path)]
            if external_scss_source_path.exists():
                include_paths.append(str(external_scss_source_path))

        if not entry_file.exists():
            self.stderr.write(f'Entry file not found: {entry_file}')
            return

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

        output_file = output_dir / 'django_spire.css'
        output_file.write_bytes(css_content.encode('utf-8'))

        self.stdout.write(self.style.SUCCESS(f'Compiled successfully: {output_file}'))

    @staticmethod
    def _get_django_spire_scss_source_path() -> Path:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / 'static' / 'django_spire' / 'scss'
            if candidate.exists():
                return candidate

        message = 'Could not locate django-spire SCSS source directory.'
        raise FileNotFoundError(message)

    @staticmethod
    def _get_external_scss_source_path() -> Path:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root:
            return Path(static_root, 'django_spire', 'scss')

        staticfiles_dir = getattr(settings, 'STATICFILES_DIRS', [])
        if staticfiles_dir:
            first_dir = staticfiles_dir[0]
            if isinstance(first_dir, (str, Path)):
                return Path(first_dir) / 'scss'

        return Path('static') / 'django_spire' / 'scss'

    @staticmethod
    def _get_default_output_dir() -> Path:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root:
            return Path(static_root, 'django_spire', 'css')

        staticfiles_dir = getattr(settings, 'STATICFILES_DIRS', [])
        if staticfiles_dir:
            first_dir = staticfiles_dir[0]
            if isinstance(first_dir, (str, Path)):
                return Path(first_dir) / 'css'

        return Path('static') / 'django_spire' / 'css'

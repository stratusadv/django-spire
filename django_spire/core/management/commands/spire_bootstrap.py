from __future__ import annotations

import shutil

from typing_extensions import TYPE_CHECKING

from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError
)

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from pathlib import Path


class Command(BaseCommand):
    help = 'Create a custom Spire app.'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            'app_name',
            help='Name of the application to create',
            type=str
        )

    def handle(self, *_args, **kwargs) -> None:
        root = settings.BASE_DIR

        app_name = kwargs['app_name']

        app_directory = root / 'django_spire/template/app'
        templates_directory = root / 'django_spire/template/templates'

        new_app_path = root / 'django_spire' / app_name
        new_templates_path = root / 'django_spire' / 'templates'

        if not app_directory.exists() or not templates_directory.exists():
            message = (
                'Template directories do not exist. Please ensure both "app" and '
                '"templates" exist in "django_spire/template/".'
            )

            raise CommandError(message)

        if new_app_path.exists():
            message = f'The app "{app_name}" already exists.'
            raise CommandError(message)

        shutil.copytree(app_directory, new_app_path)
        shutil.copytree(templates_directory, new_templates_path)

        self.replace_app_name(new_app_path, app_name)
        self.replace_app_name(new_templates_path, app_name)

        message = self.style.SUCCESS(f"Successfully created app '{app_name}'.")
        self.stdout.write(message)

    def replace_app_name(self, directory: Path, app_name: str) -> None:
        for path in directory.rglob('*'):
            if path.is_file():
                self.replace_content(path, app_name)
                self.rename_file(path, app_name)

    def replace_content(self, path: Path, app_name: str) -> None:
        with open(path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        content = (
            content
            .replace('Placeholder', app_name.capitalize())
            .replace('Placeholders', app_name.capitalize() + 's')
            .replace('placeholder', app_name.lower())
            .replace('placeholders', app_name.lower() + 's')
        )

        with open(path, 'w') as handle:
            handle.write(content)

    def rename_file(self, path: Path, app_name: str) -> None:
        app_name_lowercase = app_name.lower()

        filename = (
            path
            .name
            .replace('placeholder', app_name_lowercase)
            .replace('placeholders', app_name_lowercase + 's')
        )

        if filename != path.name:
            new_path = path.parent / filename
            path.rename(new_path)

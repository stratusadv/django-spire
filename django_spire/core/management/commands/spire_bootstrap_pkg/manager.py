import shutil

from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError

from django_spire.core.management.commands.spire_bootstrap_pkg.processor import (
        AppTemplateProcessor,
        HTMLTemplateProcessor
)
from django_spire.core.management.commands.spire_bootstrap_pkg.reporter import Reporter


class AppManager:
    def __init__(self, base: Path, template: Path):
        self.base = base
        self.template = template

    def get_valid_root_apps(self) -> set[str]:
        return {
            app.split('.')[0]
            for app in settings.INSTALLED_APPS
            if '.' in app and app.split('.')[0] != 'django'
        }

    def is_valid_root_apps(self, components: list[str]) -> None:
        valid = self.get_valid_root_apps()
        root = components[0]

        if root not in valid:
            message = (
                f'Invalid root app "{root}". '
                f'The following are valid root apps: {", ".join(valid)}.'
            )

            raise CommandError(message)

    def validate_app_name_format(self, app: str) -> None:
        if '.' not in app:
            message = (
                'Invalid app name format. '
                'The app path must use dot notation (e.g., "parent.child").'
            )

            raise CommandError(message)

    def parse_app_name(self, app: str) -> list[str]:
        return app.split('.') if '.' in app else [app]

    def get_missing_components(
        self,
        components: list[str],
        registered_apps: list[str]
    ) -> list[str]:
        missing = []

        total = len(components)

        for i in range(total):
            app = '.'.join(components[: i + 1])

            if app not in registered_apps and i > 0:
                missing.append(app)

        return missing

    def create_custom_app(
        self,
        app: str,
        processor: AppTemplateProcessor,
        reporter: Reporter
    ) -> None:
        components = app.split('.')
        destination = self.base.joinpath(*components)

        if destination.exists() and any(destination.iterdir()):
            reporter.report_app_exists(app, destination)
            return

        reporter.report_creating_app(app, destination)
        destination.mkdir(parents=True, exist_ok=True)

        if not self.template.exists():
            message = (
                f'Template directory "{self.template}" is missing. '
                'Ensure you have a valid app template.'
            )

            raise CommandError(message)

        shutil.copytree(
            self.template,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc')
        )

        processor.replace_app_name(destination, components)
        reporter.report_app_creation_success(app)


class HTMLTemplateManager:
    def __init__(self, base: Path, template: Path):
        self.base = base
        self.template = template

    def create_custom_templates(
        self,
        app: str,
        processor: HTMLTemplateProcessor,
        reporter: Reporter
    ) -> None:
        components = app.split('.')[1:]
        destination = self.base.joinpath(*components)

        if destination.exists() and any(destination.iterdir()):
            reporter.report_templates_exist(app, destination)
            return

        reporter.report_creating_templates(app, destination)
        destination.mkdir(parents=True, exist_ok=True)

        if not self.template.exists():
            message = (
                f'Template directory "{self.template}" is missing. '
                'Ensure you have a valid templates template.'
            )

            raise CommandError(message)

        shutil.copytree(
            self.template,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc')
        )

        processor.replace_template_names(destination, components)
        reporter.report_templates_creation_success(app)

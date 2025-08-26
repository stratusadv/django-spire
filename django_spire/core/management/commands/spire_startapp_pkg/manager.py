from __future__ import annotations

import shutil

from typing_extensions import TYPE_CHECKING

from django.conf import settings
from django.core.management.base import CommandError

if TYPE_CHECKING:
    from pathlib import Path

    from django_spire.core.management.commands.spire_startapp_pkg.processor import (
        AppTemplateProcessor,
        HTMLTemplateProcessor
    )
    from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter


class BaseTemplateManager:
    def __init__(self, base: Path, template: Path):
        self.base = base
        self.template = template

    def _get_destination(self, components: list[str]) -> Path:
        return self.base.joinpath(*components)

    def _report_exists(self, app: str, destination: Path, reporter: Reporter) -> None:
        raise NotImplementedError

    def _report_creating(self, app: str, destination: Path, reporter: Reporter) -> None:
        raise NotImplementedError

    def _report_success(self, app: str, reporter: Reporter) -> None:
        raise NotImplementedError

    def _create_entity(
        self,
        app: str,
        components: list[str],
        processor_method: callable,
        reporter: Reporter,
        missing_template_message: str
    ) -> None:
        destination = self._get_destination(components)

        if destination.exists() and any(destination.iterdir()):
            self._report_exists(app, destination, reporter)
            return

        self._report_creating(app, destination, reporter)
        destination.mkdir(parents=True, exist_ok=True)

        if not self.template.exists():
            raise CommandError(missing_template_message)

        shutil.copytree(
            self.template,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc')
        )

        processor_method(destination, components)
        self._report_success(app, reporter)


class AppManager(BaseTemplateManager):
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
        registry: list[str]
    ) -> list[str]:
        missing = []
        total = len(components)

        for i in range(total):
            component = '.'.join(components[: i + 1])

            if component not in registry and i > 0:
                missing.append(component)

        return missing

    def _report_exists(self, app: str, destination: Pathx, reporter: Reporter) -> None:
        reporter.report_app_exists(app, destination)

    def _report_creating(self, app: str, destination: Path, reporter: Reporter) -> None:
        reporter.report_creating_app(app, destination)

    def _report_success(self, app: str, reporter: Reporter) -> None:
        reporter.report_app_creation_success(app)

    def create_custom_app(
        self,
        app: str,
        processor: AppTemplateProcessor,
        reporter: Reporter
    ) -> None:
        components = app.split('.')

        message = (
            f'Template directory "{self.template}" is missing. '
            'Ensure you have a valid app template.'
        )

        self._create_entity(
            app,
            components,
            processor.replace_app_name,
            reporter,
            message
        )


class HTMLTemplateManager(BaseTemplateManager):
    def _report_exists(self, app: str, destination: Path, reporter: Reporter) -> None:
        reporter.report_templates_exist(app, destination)

    def _report_creating(self, app: str, destination: Path, reporter: Reporter) -> None:
        reporter.report_creating_templates(app, destination)

    def _report_success(self, app: str, reporter: Reporter) -> None:
        reporter.report_templates_creation_success(app)

    def create_custom_templates(
        self,
        app: str,
        processor: HTMLTemplateProcessor,
        reporter: Reporter
    ) -> None:
        components = app.split('.')[1:]

        message = (
            f'Template directory "{self.template}" is missing. '
            'Ensure you have a valid templates template.'
        )

        self._create_entity(
            app,
            components,
            processor.replace_template_names,
            reporter,
            message
        )

from __future__ import annotations

from typing_extensions import Callable, TYPE_CHECKING

from django_spire.core.management.commands.spire_startapp_pkg.constants import (
    INDENTATION,
    ICON_FOLDER_OPEN,
    ICON_FOLDER_CLOSED,
    ICON_FILE
)
from django_spire.core.management.commands.spire_startapp_pkg.maps import generate_replacement_map

if TYPE_CHECKING:
    from pathlib import Path

    from django.core.management.base import BaseCommand


class Reporter:
    def __init__(self, command: BaseCommand):
        self.command = command

    def _apply_replacement(self, name: str, replacement: dict[str, str]) -> str:
        for old, new in replacement.items():
            name = name.replace(old, new)

        return name

    def _report_tree_structure(
        self,
        title: str,
        base: Path,
        components: list[str],
        registry: list[str],
        template: Path,
        formatter: Callable[[Path], str],
        transformation: Callable[[int, str], str] = lambda _, component: component,
    ) -> None:
        self.command.stdout.write(title)
        current = base

        for i, component in enumerate(components):
            latest = components[: i + 1]
            replacement = generate_replacement_map(latest)

            component = transformation(i, component)
            current = current / component
            app = '.'.join(latest)
            indent = INDENTATION * i

            self.command.stdout.write(f'{indent}{ICON_FOLDER_OPEN} {component}/')

            if i == len(components) - 1 and app not in registry and template.exists():
                local_formatter = lambda item: (
                    item.name
                    if item.is_dir()
                    else self._apply_replacement(item.name, replacement)
                )

                self._show_tree_from_template(template, indent + INDENTATION, local_formatter)

    def _show_tree_from_template(
        self,
        template: Path,
        indent: str,
        formatter: Callable[[Path], str]
    ) -> None:
        ignore = {'__init__.py', '__pycache__'}

        key = lambda p: (
            p.is_file(),
            p.name.lower()
        )

        items = sorted(template.iterdir(), key=key)

        for item in items:
            if item.name in ignore:
                continue

            icon = ICON_FOLDER_CLOSED if item.is_dir() else ICON_FILE
            self.command.stdout.write(f'{indent}{icon} {formatter(item)}')

            if item.is_dir():
                self._show_tree_from_template(
                    item,
                    indent + INDENTATION,
                    formatter
                )

    def report_app_tree_structure(
        self,
        base: Path,
        components: list[str],
        registry: list[str],
        template: Path
    ) -> None:
        formatter = lambda item: item.name
        transformation = lambda _, component: component

        self._report_tree_structure(
            title='\nThe following app(s) will be created:\n\n',
            base=base,
            components=components,
            registry=registry,
            template=template,
            formatter=formatter,
            transformation=transformation,
        )

    def report_html_tree_structure(
        self,
        base: Path,
        components: list[str],
        registry: list[str],
        template: Path
    ) -> None:
        replacement = generate_replacement_map(components)

        formatter = lambda item: (
            item.name
            if item.is_dir()
            else self._apply_replacement(item.name, replacement)
        )

        transformation = (
            lambda i, component:
            'templates' if i == 0 else component
        )

        self._report_tree_structure(
            title='\nThe following template(s) will be created:\n\n',
            base=base,
            components=components,
            registry=registry,
            template=template,
            formatter=formatter,
            transformation=transformation,
        )

    def prompt_for_confirmation(self, message: str) -> bool:
        return input(message).strip().lower() == 'y'

    def report_missing_components(self, missing_components: list[str]) -> None:
        self.command.stdout.write(self.command.style.WARNING('The following are not registered apps:'))
        self.command.stdout.write('\n'.join(f' - {app}' for app in missing_components))

    def report_installed_apps_suggestion(self, missing_components: list[str]) -> None:
        self.command.stdout.write(self.command.style.NOTICE('\nPlease add the following to INSTALLED_APPS in settings.py:'))
        self.command.stdout.write(f'\n {missing_components[-1]}')
        # self.command.stdout.write('\n'.join(f'"{app}"' for app in missing_components))

    def report_app_creation_success(self, app: str) -> None:
        message = f'Successfully created app: {app}'
        self.write(message, self.command.style.SUCCESS)

    def report_app_exists(self, app: str, destination: Path) -> None:
        message = f'The app "{app}" already exists at {destination}'
        self.write(message, self.command.style.WARNING)

    def report_creating_app(self, app: str, destination: Path) -> None:
        message = f'Creating app "{app}" at {destination}'
        self.write(message, self.command.style.NOTICE)

    def report_templates_exist(self, app: str, destination: Path) -> None:
        message = f'The templates for app "{app}" already exist at {destination}'
        self.write(message, self.command.style.WARNING)

    def report_creating_templates(self, app: str, destination: Path) -> None:
        message = f'Creating templates for app "{app}" at {destination}'
        self.write(message, self.command.style.NOTICE)

    def report_templates_creation_success(self, app: str) -> None:
        message = f'Successfully created templates for app: {app}'
        self.write(message, self.command.style.SUCCESS)

    def write(self, message: str, func: Callable[[str], str]) -> None:
        self.command.stdout.write(func(message))

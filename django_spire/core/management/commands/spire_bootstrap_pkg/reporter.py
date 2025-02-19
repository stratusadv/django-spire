from pathlib import Path
from typing_extensions import Callable

from django.core.management.base import BaseCommand

from django_spire.core.management.commands.spire_bootstrap_pkg.maps import generate_replacement_map


INDENT = '    '


class Reporter:
    def __init__(self, command: BaseCommand):
        self.command = command

    def prompt_for_confirmation(self, message: str) -> bool:
        return input(message).strip().lower() == 'y'

    def write(self, message: str, func: Callable[[str], str]) -> None:
        self.command.stdout.write(func(message))

    def report_missing_components(self, missing_components: list[str]) -> None:
        self.command.stdout.write(self.command.style.WARNING('The following are not registered apps:'))
        self.command.stdout.write('\n'.join(f' - {app}' for app in missing_components))

    def report_installed_apps_suggestion(self, missing_components: list[str]) -> None:
        self.command.stdout.write(self.command.style.NOTICE('\nPlease add the following to INSTALLED_APPS in settings.py:'))
        self.command.stdout.write('\n'.join(f'"{app}"' for app in missing_components))

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

    def report_app_tree_structure(self, base: Path, components: list[str], registered_apps: list[str], template: Path) -> None:
        self.command.stdout.write('\nThe following app(s) will be created:\n\n')

        current = base

        for i, component in enumerate(components):
            current = current / component

            app = '.'.join(components[: i + 1])
            indent = INDENT * i

            self.command.stdout.write(f'{indent}📂 {component}/')

            if i > 0 and app not in registered_apps and template.exists():
                self.show_app_tree_from_template(template, indent=indent + INDENT)

    def report_html_tree_structure(self, base: Path, components: list[str], registered_apps: list[str], template: Path) -> None:
        replacements = generate_replacement_map(components)
        self.command.stdout.write('\nThe following template(s) will be created:\n\n')

        current = base

        for i, component in enumerate(components):
            if i == 0:
                component = 'templates'

            current = current / component
            app = '.'.join(components[: i + 1])
            indent = INDENT * i

            self.command.stdout.write(f'{indent}📂 {component}/')

            if i > 0 and app not in registered_apps and template.exists():
                self.show_html_tree_from_template(template, indent=indent + INDENT, replacements=replacements)

    def show_app_tree_from_template(self, template_dir: Path, indent: str = '') -> None:
        ignore = {'__init__.py', '__pycache__'}

        items = sorted(
            template_dir.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower())
        )

        for item in items:
            if item.name in ignore:
                continue

            self.command.stdout.write(f'{indent}{"📁" if item.is_dir() else "📄"} {item.name}')

            if item.is_dir():
                self.show_app_tree_from_template(item, indent=indent + INDENT)

    def show_html_tree_from_template(self, template_dir: Path, indent: str, replacements: dict[str, str]) -> None:
        ignore = {'__init__.py', '__pycache__'}

        items = sorted(
            template_dir.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower())
        )

        for item in items:
            if item.name in ignore:
                continue

            name = item.name

            if not item.is_dir():
                for old, new in replacements.items():
                    name = name.replace(old, new)

            self.command.stdout.write(f'{indent}{"📁" if item.is_dir() else "📄"} {name}')

            if item.is_dir():
                self.show_html_tree_from_template(item, indent=indent + INDENT, replacements=replacements)

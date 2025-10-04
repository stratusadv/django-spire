from __future__ import annotations

from string import Template
from typing import Protocol, TYPE_CHECKING

from django_spire.core.management.commands.spire_startapp_pkg.maps import generate_replacement_map

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Callable

    from django.core.management.base import BaseCommand


class ReporterInterface(Protocol):
    """
    Protocol defining the interface for reporting and user interaction.

    This protocol specifies methods for displaying messages, prompts,
    and tree structures to the user during app creation.
    """

    def prompt_confirmation(self, message: str) -> bool: ...
    def report_app_creation_success(self, app: str) -> None: ...
    def report_app_exists(self, app: str, destination: Path) -> None: ...
    def report_creating_app(self, app: str, destination: Path) -> None: ...
    def report_creating_templates(self, app: str, destination: Path) -> None: ...
    def report_installed_apps_suggestion(self, missing_components: list[str]) -> None: ...
    def report_missing_components(self, missing_components: list[str]) -> None: ...
    def report_templates_creation_success(self, app: str) -> None: ...
    def report_templates_exist(self, app: str, destination: Path) -> None: ...
    def write(self, message: str, style: Callable[[str], str]) -> None: ...


class Reporter:
    """
    Handles user interaction and console output for the app creation command.

    This class manages all console output including status messages, tree
    structures, confirmations, and styled text for the app creation process.
    """

    ICON_FILE = '📄'
    ICON_FOLDER_CLOSED = '📁'
    ICON_FOLDER_OPEN = '📂'
    INDENTATION = '    '

    def __init__(self, command: BaseCommand):
        """
        Initializes the reporter with a Django management command.

        :param command: Django BaseCommand instance for accessing stdout and styling.
        """

        self.command = command
        self.style_error = command.style.ERROR
        self.style_notice = command.style.NOTICE
        self.style_success = command.style.SUCCESS
        self.style_warning = command.style.WARNING

    def format_app_item(self, item: Path) -> str:
        """
        Formats an app file or directory name for display.

        Removes the .template extension from Python files.

        :param item: Path to the item to format.
        :return: Formatted item name.
        """

        return item.name.replace('.py.template', '.py')

    def format_html_item(self, item: Path, replacement: dict[str, str]) -> str:
        """
        Formats an HTML template file or directory name for display.

        Applies variable replacements and removes .template extensions.

        :param item: Path to the item to format.
        :param replacement: Dictionary of placeholder replacements.
        :return: Formatted item name with placeholders replaced.
        """

        if item.is_dir():
            return item.name

        template = Template(item.name)
        filename = template.safe_substitute(replacement)

        if filename.endswith('.template'):
            filename = filename.replace('.template', '')

        return filename

    def prompt_confirmation(self, message: str) -> bool:
        """
        Prompts the user for yes/no confirmation.

        :param message: Confirmation prompt message.
        :return: True if user responds with 'y', False otherwise.
        """

        return input(message).strip().lower() == 'y'

    def report_app_creation_success(self, app: str) -> None:
        """
        Reports successful creation of an app.

        :param app: Name of the app that was created.
        """

        self.write(f'Successfully created app: {app}', self.style_success)

    def report_app_exists(self, app: str, destination: Path) -> None:
        """
        Reports that an app already exists at the destination.

        :param app: Name of the app.
        :param destination: Path where the app already exists.
        """

        self.write(f'The app "{app}" already exists at {destination}', self.style_warning)

    def report_creating_app(self, app: str, destination: Path) -> None:
        """
        Reports that an app is being created.

        :param app: Name of the app being created.
        :param destination: Path where the app will be created.
        """

        self.write(f'Creating app "{app}" at {destination}', self.style_notice)

    def report_creating_templates(self, app: str, destination: Path) -> None:
        """
        Reports that templates are being created for an app.

        :param app: Name of the app.
        :param destination: Path where templates will be created.
        """

        self.write(f'Creating templates for app "{app}" at {destination}', self.style_notice)

    def report_installed_apps_suggestion(self, missing_components: list[str]) -> None:
        """
        Suggests which app to add to INSTALLED_APPS in settings.py.

        :param missing_components: List of missing app components.
        """

        self.write('\nPlease add the following to INSTALLED_APPS in settings.py:', self.style_notice)
        self.write(f'\n {missing_components[-1]}', lambda x: x)

    def report_missing_components(self, missing_components: list[str]) -> None:
        """
        Reports which app components are not yet registered.

        :param missing_components: List of unregistered app component paths.
        """

        self.write('The following are not registered apps:', self.style_warning)
        self.write('\n'.join(f' - {app}' for app in missing_components), lambda x: x)

    def report_templates_creation_success(self, app: str) -> None:
        """
        Reports successful creation of templates for an app.

        :param app: Name of the app whose templates were created.
        """

        self.write(f'Successfully created templates for app: {app}', self.style_success)

    def report_templates_exist(self, app: str, destination: Path) -> None:
        """
        Reports that templates already exist for an app.

        :param app: Name of the app.
        :param destination: Path where templates already exist.
        """

        self.write(f'The templates for app "{app}" already exist at {destination}', self.style_warning)

    def report_tree_structure(
        self,
        title: str,
        base: Path,
        components: list[str],
        registry: list[str],
        template: Path,
        formatter: Callable[[Path], str],
        transformation: Callable[[int, str], str] | None = None,
    ) -> None:
        """
        Displays a tree structure of files and directories that will be created.

        Shows a hierarchical view of the app structure with appropriate icons
        and formatting for files and directories.

        :param title: Title to display above the tree structure.
        :param base: Base directory path.
        :param components: List of app path components.
        :param registry: List of registered apps.
        :param template: Path to template directory.
        :param formatter: Function to format item names for display.
        :param transformation: Optional function to transform component names.
        """

        if transformation is None:
            transformation = self.transform_app_component

        self.command.stdout.write(title)
        current = base

        for i, component in enumerate(components):
            latest = components[: i + 1]
            replacement = generate_replacement_map(latest)

            component = transformation(i, component)
            current = current / component
            app = '.'.join(latest)
            indent = self.INDENTATION * i

            self.command.stdout.write(f'{indent}{self.ICON_FOLDER_OPEN} {component}/')

            if i == len(components) - 1 and app not in registry and template.exists():
                def local_formatter(item: Path, mapping: dict[str, str] = replacement) -> str:
                    base_name = formatter(item)
                    return self._apply_replacement(base_name, mapping)

                self._show_tree_from_template(template, indent + self.INDENTATION, local_formatter)

    def transform_app_component(self, _index: int, component: str) -> str:
        """
        Transforms an app component name (default: no transformation).

        :param _index: Index of the component in the path.
        :param component: Component name to transform.
        :return: Transformed component name.
        """

        return component

    def transform_html_component(self, index: int, component: str) -> str:
        """
        Transforms an HTML component name (replaces first component with 'templates').

        :param index: Index of the component in the path.
        :param component: Component name to transform.
        :return: Transformed component name.
        """

        return 'templates' if index == 0 else component

    def write(self, message: str, style: Callable[[str], str]) -> None:
        """
        Writes a styled message to the console.

        :param message: Message to display.
        :param style: Styling function to apply to the message.
        """

        self.command.stdout.write(style(message))

    def _apply_replacement(self, name: str, replacement: dict[str, str]) -> str:
        """
        Applies placeholder replacements to a name string.

        :param name: String containing placeholders.
        :param replacement: Dictionary mapping placeholders to values.
        :return: String with placeholders replaced.
        """

        for old, new in replacement.items():
            name = name.replace(old, new)
        return name

    def _show_tree_from_template(
        self,
        template: Path,
        indent: str,
        formatter: Callable[[Path], str]
    ) -> None:
        """
        Recursively displays a tree structure from a template directory.

        :param template: Template directory path to display.
        :param indent: Current indentation level.
        :param formatter: Function to format item names.
        """

        ignore = {'__init__.py', '__pycache__'}

        items = sorted(template.iterdir(), key=self._sort_template_items)

        for item in items:
            if item.name in ignore:
                continue

            icon = self.ICON_FOLDER_CLOSED if item.is_dir() else self.ICON_FILE
            self.command.stdout.write(f'{indent}{icon} {formatter(item)}')

            if item.is_dir():
                self._show_tree_from_template(
                    item,
                    indent + self.INDENTATION,
                    formatter
                )

    def _sort_template_items(self, path: Path) -> tuple[bool, str]:
        """
        Sorts template items with directories first, then by name.

        :param path: Path to sort.
        :return: Tuple for sorting (is_file, lowercase_name).
        """

        return (path.is_file(), path.name.lower())

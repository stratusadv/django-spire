from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter


class PermissionInheritanceHandler:
    """
    Handles permission inheritance configuration for nested Django apps.

    This class manages the interactive collection of permission inheritance
    settings when creating child apps that may inherit permissions from parent apps.
    """

    def __init__(self, reporter: Reporter):
        """
        Initializes the handler with a reporter for user interaction.

        :param reporter: Reporter instance for displaying prompts and messages.
        """

        self.reporter = reporter

    def collect_inheritance_data(self, components: list[str]) -> dict[str, Any]:
        """
        Collects permission inheritance configuration from the user.

        Prompts the user to determine if the new app should inherit permissions
        from its parent app, and if so, collects the necessary parent model information.

        :param components: List of app path components.
        :return: Dictionary containing inheritance configuration data.
        """

        if len(components) <= 2:
            return {
                'inherit_permissions': False,
                'parent_model_instance_name': '',
                'parent_permission_prefix': '',
            }

        if not self._should_inherit_permissions():
            return {
                'inherit_permissions': False,
                'parent_model_instance_name': '',
                'parent_permission_prefix': '',
            }

        return {
            'inherit_permissions': True,
            'parent_model_instance_name': self._collect_parent_model_instance_name(components),
            'parent_model_path': self._collect_parent_model_path(components),
            'parent_permission_prefix': self._collect_parent_permission_prefix(components),
        }

    def _build_default_parent_model_path(self, components: list[str]) -> str:
        """
        Builds a default parent model path based on app components.

        :param components: List of app path components.
        :return: Default parent model path string.
        """

        parent_name = components[-2]
        parent_model_class = ''.join(word.title() for word in parent_name.split('_'))
        return '.'.join(components[:-1]) + f'.models.{parent_model_class}'

    def _build_default_parent_permission_prefix(self, components: list[str]) -> str:
        """
        Builds a default parent permission prefix based on app components.

        :param components: List of app path components.
        :return: Default permission prefix string.
        """

        parent_parts = components[1:-1]
        return '_'.join(parent_parts).lower()

    def _collect_parent_model_instance_name(self, components: list[str]) -> str:
        """
        Prompts the user for the parent model instance name.

        :param components: List of app path components.
        :return: User-provided or default parent model instance name.
        """

        parent_name = components[-2]
        default = parent_name.lower()

        self.reporter.write(
            f'\nEnter the parent model instance name (default: "{default}")',
            self.reporter.style_notice
        )

        user_input = input('Press Enter to use default or type a custom name: ').strip()
        return user_input if user_input else default

    def _collect_parent_model_path(self, components: list[str]) -> str:
        """
        Prompts the user for the parent model path.

        :param components: List of app path components.
        :return: User-provided or default parent model path.
        """

        default = self._build_default_parent_model_path(components)

        self.reporter.write(
            f'\nEnter the parent model path (default: "{default}")',
            self.reporter.style_notice
        )

        user_input = input('Press Enter to use default or type a custom path: ').strip()
        return user_input if user_input else default

    def _collect_parent_permission_prefix(self, components: list[str]) -> str:
        """
        Prompts the user for the parent permission prefix.

        :param components: List of app path components.
        :return: User-provided or default parent permission prefix.
        """

        default = self._build_default_parent_permission_prefix(components)

        self.reporter.write(
            f'\nEnter the parent permission prefix (default: "{default}")',
            self.reporter.style_notice
        )

        user_input = input('Press Enter to use default or type a custom prefix: ').strip()
        return user_input if user_input else default

    def _should_inherit_permissions(self) -> bool:
        """
        Prompts the user to confirm permission inheritance.

        :return: True if user wants to inherit permissions, False otherwise.
        """

        self.reporter.write('\nDo you want this app to inherit permissions from its parent? (y/n)', self.reporter.style_notice)
        user_input = input('Default is "n": ').strip().lower()
        return user_input == 'y'

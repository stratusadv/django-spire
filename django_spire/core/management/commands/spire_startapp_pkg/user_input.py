from __future__ import annotations

import re

from typing import TYPE_CHECKING

from django.core.management.base import CommandError

if TYPE_CHECKING:
    from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter
    from django_spire.core.management.commands.spire_startapp_pkg.validator import AppValidator


class UserInputCollector:
    """
    Collects user input for Django app creation through an interactive wizard.

    This class guides users through a step-by-step process to gather all
    necessary configuration for creating a new Django app.
    """

    def __init__(self, reporter: Reporter, validator: AppValidator):
        """
        Initializes the collector with a reporter and validator.

        :param reporter: Reporter instance for displaying prompts and messages.
        :param validator: Validator for checking user input validity.
        """

        self.reporter = reporter
        self.validator = validator

    def collect_all_inputs(self) -> dict[str, str]:
        """
        Collects all required user inputs for app creation.

        Guides the user through an 8-step wizard to gather app path, names,
        labels, and configuration options.

        :return: Dictionary containing all collected user inputs.
        """

        self.reporter.write('\n[App Creation Wizard]\n\n', self.reporter.style_success)

        app_path = self._collect_app_path()
        components = app_path.split('.')

        app_name = self._collect_app_name(components)
        app_label = self._collect_app_label(components, app_name)
        model_name = self._collect_model_name(app_name)
        model_name_plural = self._collect_model_name_plural(model_name)
        db_table_name = self._collect_db_table_name(components, app_name)  # Changed from app_label to components, app_name
        model_permission_path = self._collect_model_permission_path(app_path, model_name)

        permission_data = self._collect_permission_inheritance(components)

        verbose_name, verbose_name_plural = self._derive_verbose_names(model_name, model_name_plural)

        return {
            'app_path': app_path,
            'app_name': app_name,
            'model_name': model_name,
            'model_name_plural': model_name_plural,
            'app_label': app_label,
            'db_table_name': db_table_name,
            'model_permission_path': model_permission_path,
            'verbose_name': verbose_name,
            'verbose_name_plural': verbose_name_plural,
            **permission_data,
        }

    def _collect_app_label(self, components: list[str], app_name: str) -> str:
        """
        Prompts the user for the Django app label.

        :param components: List of app path components.
        :param app_name: Name of the app.
        :return: User-provided or default app label.
        """

        immediate_parent = components[-2] if len(components) > 2 else None
        default = immediate_parent.lower() + '_' + app_name.lower() if immediate_parent else app_name.lower()
        return self._collect_input('Enter the app label', default, '3/8')

    def _collect_app_name(self, components: list[str]) -> str:
        """
        Prompts the user for the app name.

        :param components: List of app path components.
        :return: User-provided or default app name.
        """

        default = components[-1]
        return self._collect_input('Enter the app name', default, '2/8')

    def _collect_app_path(self) -> str:
        """
        Prompts the user for the app path and validates it.

        :return: Validated app path in dot notation.
        :raises CommandError: If the app path is empty or invalid.
        """

        app_path = self._collect_simple_input('Enter the app path (e.g., "app.human_resource.employee.skill")', '1/8')

        if not app_path:
            self.reporter.write('\n', self.reporter.style_notice)

            message = 'The app path is required'
            raise CommandError(message)

        components = app_path.split('.')
        self.validator.validate_app_path(components)

        return app_path

    def _collect_db_table_name(self, components: list[str], app_name: str) -> str:
        """
        Prompts the user for the database table name.

        :param components: List of app path components.
        :param app_name: Name of the app.
        :return: User-provided or default database table name.
        """

        parent_parts = components[1:-1] if len(components) > 1 else []
        default = '_'.join(parent_parts).lower() + '_' + app_name.lower() if parent_parts else app_name.lower()
        return self._collect_input('Enter the database table name', default, '6/8')

    def _collect_input(self, prompt: str, default: str, step_number: str) -> str:
        """
        Prompts the user for input with a default value.

        :param prompt: Prompt message to display.
        :param default: Default value if user presses Enter.
        :param step_number: Step number in the wizard (e.g., '1/8').
        :return: User-provided input or default value.
        """

        self.reporter.write(f'\n[{step_number}]: {prompt} (default: "{default}")', self.reporter.style_notice)
        user_input = input('Press Enter to use default or type a custom value: ').strip()
        return user_input if user_input else default

    def _collect_model_name(self, app_name: str) -> str:
        """
        Prompts the user for the model class name.

        :param app_name: App name to derive default from.
        :return: User-provided or default model name in TitleCase.
        """

        default = ''.join(word.title() for word in app_name.split('_'))
        return self._collect_input('Enter the model name', default, '4/8')

    def _collect_model_name_plural(self, model_name: str) -> str:
        """
        Prompts the user for the plural form of the model name.

        :param model_name: Singular model name.
        :return: User-provided or default plural model name.
        """

        default = model_name + 's'
        return self._collect_input('Enter the model name plural', default, '5/8')

    def _collect_model_permission_path(self, app_path: str, model_name: str) -> str:
        """
        Prompts the user for the model permission path.

        :param app_path: Dot-separated app path.
        :param model_name: Model class name.
        :return: User-provided or default model permission path.
        """

        default = f'{app_path}.models.{model_name}'
        return self._collect_input('Enter the model permission path', default, '7/8')

    def _collect_permission_inheritance(self, components: list[str]) -> dict[str, str]:
        """
        Collects permission inheritance configuration if applicable.

        Prompts the user about inheriting permissions from parent apps
        and collects necessary parent model information.

        :param components: List of app path components.
        :return: Dictionary containing permission inheritance settings.
        """

        if len(components) <= 1:
            return {'inherit_permissions': False, 'parent_permission_prefix': '', 'parent_model_instance_name': ''}

        if not self._should_inherit_permissions():
            return {'inherit_permissions': False, 'parent_permission_prefix': '', 'parent_model_instance_name': ''}

        parent_parts = components[1:-1]
        parent_name = components[-2]
        parent_model_class = ''.join(word.title() for word in parent_name.split('_'))

        self.reporter.write('\n[Permission Inheritance Configuration]\n', self.reporter.style_notice)

        return {
            'inherit_permissions': True,
            'parent_permission_prefix': self._collect_input(
                'Enter the parent permission prefix',
                '_'.join(parent_parts).lower(),
                '1/3'
            ),
            'parent_model_instance_name': self._collect_input(
                'Enter the parent model instance name',
                parent_name.lower(),
                '2/3'
            ),
            'parent_model_path': self._collect_input(
                'Enter the parent model path',
                '.'.join(components[:-1]) + f'.models.{parent_model_class}',
                '3/3'
            ),
        }

    def _collect_simple_input(self, prompt: str, step_number: str) -> str:
        """
        Prompts the user for simple input without a default value.

        :param prompt: Prompt message to display.
        :param step_number: Step number in the wizard.
        :return: User-provided input.
        """

        return input(f'[{step_number}]: {prompt}: ').strip()

    def _derive_verbose_names(self, model_name: str, model_name_plural: str) -> tuple[str, str]:
        """
        Derives human-readable verbose names from model names.

        Converts CamelCase model names to space-separated words.

        :param model_name: Singular model name in CamelCase.
        :param model_name_plural: Plural model name in CamelCase.
        :return: Tuple of (verbose_name, verbose_name_plural).
        """

        verbose_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', model_name)
        verbose_name_plural = re.sub(r'(?<!^)(?=[A-Z])', ' ', model_name_plural)
        return verbose_name, verbose_name_plural

    def _should_inherit_permissions(self) -> bool:
        """
        Prompts the user to confirm permission inheritance.

        :return: True if user wants to inherit permissions, False otherwise.
        """

        self.reporter.write('\n[8/8]: Do you want this app to inherit permissions from its parent? (y/n)', self.reporter.style_notice)
        user_input = input('Default is "n": ').strip().lower()
        return user_input == 'y'

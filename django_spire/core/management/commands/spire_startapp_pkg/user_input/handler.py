from __future__ import annotations

import re

from typing import TYPE_CHECKING

from django.core.management.base import CommandError

from django_spire.core.management.commands.spire_startapp_pkg.permissions import PermissionInheritanceHandler
from django_spire.core.management.commands.spire_startapp_pkg.user_input.validator import UserInputValidator

if TYPE_CHECKING:
    from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter


class UserInputHandler:
    def __init__(self, reporter: Reporter):
        self.reporter = reporter
        self.validator = UserInputValidator()

    def _collect_input(
        self,
        prompt: str,
        default: str,
        step_number: str
    ) -> str:
        self.reporter.write(f'\n[{step_number}]: {prompt} (default: "{default}")', self.reporter.command.style.NOTICE)
        user_input = input('Press Enter to use default or type a custom value: ').strip()
        return user_input if user_input else default

    def _collect_simple_input(
        self,
        prompt: str,
        step_number: str
    ) -> str:
        return input(f'[{step_number}]: {prompt}: ').strip()

    def collect_all_inputs(self) -> dict[str, str]:
        self.reporter.write('\n[App Creation Wizard]\n\n', self.reporter.command.style.SUCCESS)

        app_path = self.collect_app_path()
        components = app_path.split('.')

        app_name = self.collect_app_name(components)
        app_label = self.collect_app_label(components, app_name)
        model_name = self.collect_model_name(app_name)
        model_name_plural = self.collect_model_name_plural(model_name)
        db_table_name = self.collect_db_table_name(app_label)
        model_permission_path = self.collect_model_permission_path(app_path, model_name)

        permission_handler = PermissionInheritanceHandler(self.reporter)
        permission_data = permission_handler.collect_inheritance_data(components)

        verbose_name, verbose_name_plural = self.derive_verbose_names(model_name, model_name_plural)

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

    def collect_app_label(self, components: list[str], app_name: str) -> str:
        parent_parts = components[1:-1] if len(components) > 1 else []
        default = '_'.join(parent_parts).lower() + '_' + app_name.lower() if parent_parts else app_name.lower()
        return self._collect_input('Enter the app label', default, '3/8')

    def collect_app_name(self, components: list[str]) -> str:
        default = components[-1]
        return self._collect_input('Enter the app name', default, '2/8')

    def collect_app_path(self) -> str:
        app_path = self._collect_simple_input('Enter the app path (e.g., "app.human_resource.employee.skill")', '1/8')

        if not app_path:
            self.reporter.write('\n', self.reporter.command.style.NOTICE)
            raise CommandError(self.reporter.command.style.ERROR('The app path is required'))

        components = app_path.split('.')
        self.validator.check_app_exists(components)

        return app_path

    def collect_db_table_name(self, app_label: str) -> str:
        return self._collect_input('Enter the database table name', app_label, '6/8')

    def collect_model_name(self, app_name: str) -> str:
        default = ''.join(word.title() for word in app_name.split('_'))
        return self._collect_input('Enter the model name', default, '4/8')

    def collect_model_name_plural(self, model_name: str) -> str:
        default = model_name + 's'
        return self._collect_input('Enter the model name plural', default, '5/8')

    def collect_model_permission_path(self, app_path: str, model_name: str) -> str:
        default = f'{app_path}.models.{model_name}'
        return self._collect_input('Enter the model permission path', default, '7/8')

    def derive_verbose_names(self, model_name: str, model_name_plural: str) -> tuple[str, str]:
        verbose_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', model_name)
        verbose_name_plural = re.sub(r'(?<!^)(?=[A-Z])', ' ', model_name_plural)
        return verbose_name, verbose_name_plural


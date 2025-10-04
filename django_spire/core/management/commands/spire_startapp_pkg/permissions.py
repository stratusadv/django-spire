from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter


class PermissionInheritanceHandler:
    def __init__(self, reporter: Reporter):
        self.reporter = reporter

    def _build_default_parent_model_path(self, components: list[str]) -> str:
        parent_name = components[-2]
        parent_model_class = ''.join(word.title() for word in parent_name.split('_'))
        return '.'.join(components[:-1]) + f'.models.{parent_model_class}'

    def _build_default_parent_permission_prefix(self, components: list[str]) -> str:
        parent_parts = components[1:-1]
        return '_'.join(parent_parts).lower()

    def _collect_parent_model_instance_name(self, components: list[str]) -> str:
        parent_name = components[-2]
        default = parent_name.lower()

        self.reporter.write(
            f'\nEnter the parent model instance name (default: "{default}")',
            self.reporter.command.style.NOTICE
        )

        user_input = input('Press Enter to use default or type a custom name: ').strip()
        return user_input if user_input else default

    def _collect_parent_model_path(self, components: list[str]) -> str:
        default = self._build_default_parent_model_path(components)

        self.reporter.write(
            f'\nEnter the parent model path (default: "{default}")',
            self.reporter.command.style.NOTICE
        )

        user_input = input('Press Enter to use default or type a custom path: ').strip()
        return user_input if user_input else default

    def _collect_parent_permission_prefix(self, components: list[str]) -> str:
        default = self._build_default_parent_permission_prefix(components)

        self.reporter.write(
            f'\nEnter the parent permission prefix (default: "{default}")',
            self.reporter.command.style.NOTICE
        )

        user_input = input('Press Enter to use default or type a custom prefix: ').strip()
        return user_input if user_input else default

    def _should_inherit_permissions(self) -> bool:
        self.reporter.write('\n[8/8]: Do you want this app to inherit permissions from its parent? (y/n)', self.reporter.command.style.NOTICE)
        user_input = input('Default is "n": ').strip().lower()
        return user_input == 'y'

    def collect_inheritance_data(self, components: list[str]) -> dict[str, Any]:
        if len(components) <= 2:
            return {
                'inherit_permissions': False,
                'parent_permission_prefix': '',
                'parent_model_instance_name': '',
            }

        if not self._should_inherit_permissions():
            return {
                'inherit_permissions': False,
                'parent_permission_prefix': '',
                'parent_model_instance_name': '',
            }

        return {
            'inherit_permissions': True,
            'parent_permission_prefix': self._collect_parent_permission_prefix(components),
            'parent_model_instance_name': self._collect_parent_model_instance_name(components),
            'parent_model_path': self._collect_parent_model_path(components),
        }

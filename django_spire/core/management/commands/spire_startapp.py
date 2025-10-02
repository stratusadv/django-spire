from __future__ import annotations

import django_spire
import re

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_spire.core.management.commands.spire_startapp_pkg.manager import (
        AppManager,
        HTMLTemplateManager,
)
from django_spire.core.management.commands.spire_startapp_pkg.processor import (
        AppTemplateProcessor,
        HTMLTemplateProcessor
)
from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter


class Command(BaseCommand):
    help = 'Create a custom Spire app.'

    def __init__(self):
        super().__init__()

        self.app_base = Path(settings.BASE_DIR)
        self.app_template = Path(django_spire.__file__).parent / 'core/management/commands/spire_startapp_pkg/template/app'

        self.template_base = self.app_base / 'templates'
        self.html_template = Path(django_spire.__file__).parent / 'core/management/commands/spire_startapp_pkg/template/templates'

        self.app_manager = AppManager(self.app_base, self.app_template)
        self.app_processor = AppTemplateProcessor()

        self.html_manager = HTMLTemplateManager(self.template_base, self.html_template)
        self.html_processor = HTMLTemplateProcessor()

        self.reporter = Reporter(self)

    def get_app_names(self) -> list[str]:
        from django.apps import apps
        return [config.name for config in apps.get_app_configs()]

    def _get_app_path(self) -> tuple[str, list[str]]:
        app_path = input('[1/8]: Enter the app path (e.g., "app.human_resource.employee.skill"): ').strip()

        if not app_path:
            raise CommandError(self.style.ERROR('The app path is required'))

        return app_path, app_path.split('.')

    def _get_app_name(self, components: list[str]) -> str:
        default_app_name = components[-1]
        self.reporter.write(f'\n[2/8]: Enter the app name (default: "{default_app_name}")', self.style.NOTICE)
        app_name_input = input('Press Enter to use default or type a custom name: ').strip()
        return app_name_input if app_name_input else default_app_name

    def _get_app_label(self, components: list[str], app_name: str) -> str:
        parent_parts = components[1:-1] if len(components) > 1 else []
        default_app_label = '_'.join(parent_parts).lower() + '_' + app_name.lower() if parent_parts else app_name.lower()
        self.reporter.write(f'\n[3/8]: Enter the app label (default: "{default_app_label}")', self.style.NOTICE)
        app_label_input = input('Press Enter to use default or type a custom name: ').strip()
        return app_label_input if app_label_input else default_app_label

    def _get_model_name(self, app_name: str) -> str:
        default_model_name = ''.join(word.title() for word in app_name.split('_'))
        self.reporter.write(f'\n[4/8]: Enter the model name (default: "{default_model_name}")', self.style.NOTICE)
        model_name_input = input('Press Enter to use default or type a custom name: ').strip()
        return model_name_input if model_name_input else default_model_name

    def _get_model_name_plural(self, model_name: str) -> str:
        default_model_plural = model_name + 's'
        self.reporter.write(f'\n[5/8]: Enter the model name plural (default: "{default_model_plural}")', self.style.NOTICE)
        model_plural_input = input('Press Enter to use default or type a custom name: ').strip()
        return model_plural_input if model_plural_input else default_model_plural

    def _get_db_table_name(self, app_label: str) -> str:
        default_db_table = app_label
        self.reporter.write(f'\n[6/8]: Enter the database table name (default: "{default_db_table}")', self.style.NOTICE)
        db_table_input = input('Press Enter to use default or type a custom name: ').strip()
        return db_table_input if db_table_input else default_db_table

    def _get_model_permission_path(self, app_path: str, model_name: str) -> str:
        default_permission_path = f'{app_path}.models.{model_name}'
        self.reporter.write(f'\n[7/8]: Enter the model permission path (default: "{default_permission_path}")', self.style.NOTICE)
        permission_path_input = input('Press Enter to use default or type a custom path: ').strip()
        return permission_path_input if permission_path_input else default_permission_path

    def _get_is_proxy_model(self) -> bool:
        self.reporter.write('\n[8/8]: Is this a proxy model? (y/N)', self.style.NOTICE)
        is_proxy_input = input('Press Enter for No or type y for Yes: ').strip().lower()
        return is_proxy_input in ['y', 'yes']

    def _derive_verbose_names(self, model_name: str, model_name_plural: str) -> tuple[str, str]:
        verbose_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', model_name)
        verbose_name_plural = re.sub(r'(?<!^)(?=[A-Z])', ' ', model_name_plural)
        return verbose_name, verbose_name_plural

    def get_user_input(self) -> dict[str, str]:
        self.reporter.write('\n[App Creation Wizard]\n\n', self.style.SUCCESS)

        app_path, components = self._get_app_path()
        app_name = self._get_app_name(components)
        app_label = self._get_app_label(components, app_name)
        model_name = self._get_model_name(app_name)
        model_name_plural = self._get_model_name_plural(model_name)
        db_table_name = self._get_db_table_name(app_label)
        model_permission_path = self._get_model_permission_path(app_path, model_name)
        is_proxy_model = self._get_is_proxy_model()
        verbose_name, verbose_name_plural = self._derive_verbose_names(model_name, model_name_plural)

        return {
            'app_path': app_path,
            'app_name': app_name,
            'model_name': model_name,
            'model_name_plural': model_name_plural,
            'app_label': app_label,
            'db_table_name': db_table_name,
            'model_permission_path': model_permission_path,
            'is_proxy_model': is_proxy_model,
            'verbose_name': verbose_name,
            'verbose_name_plural': verbose_name_plural,
        }

    def handle(self, *_args, **kwargs) -> None:
        user_inputs = self.get_user_input()
        app = user_inputs['app_path']

        self.app_manager.validate_app_name_format(app)

        components = self.app_manager.parse_app_name(app)
        self.app_manager.is_valid_root_apps(components)

        registry = self.get_app_names()

        self.reporter.write(
            f'\nChecking app components: {components}\n',
            self.style.NOTICE
        )

        missing = self.app_manager.get_missing_components(components, registry)

        if missing:
            self.reporter.report_missing_components(missing)
            self.reporter.report_app_tree_structure(self.app_base, components, registry, self.app_template)
            # self.reporter.report_html_tree_structure(self.template_base, components, registry, self.html_template)

            if not self.reporter.prompt_for_confirmation('\nProceed with app creation? (y/n): '):
                self.reporter.write('App creation aborted.', self.style.ERROR)
                return

            for module in [missing[-1]]:
                self.app_manager.create_custom_app(
                    module,
                    self.app_processor,
                    self.reporter,
                    user_inputs
                )

                # self.html_manager.create_custom_templates(module, self.html_processor, self.reporter)

            self.reporter.report_installed_apps_suggestion(missing)
        else:
            self.reporter.write('All component(s) exist.', self.style.SUCCESS)

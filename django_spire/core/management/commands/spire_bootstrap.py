import argparse
import django_spire

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_spire.core.management.commands.spire_bootstrap_pkg.manager import (
        AppManager,
        HTMLTemplateManager,
)
from django_spire.core.management.commands.spire_bootstrap_pkg.processor import (
        AppTemplateProcessor,
        HTMLTemplateProcessor
)
from django_spire.core.management.commands.spire_bootstrap_pkg.reporter import Reporter


class Command(BaseCommand):
    help = 'Create a custom Spire app.'

    def __init__(self):
        super().__init__()

        self.app_base = Path(settings.BASE_DIR)
        self.app_template = Path(django_spire.__file__).parent / 'template/app'

        self.template_base = self.app_base / 'templates'
        self.html_template = Path(django_spire.__file__).parent / 'template/templates'

        self.app_manager = AppManager(self.app_base, self.app_template)
        self.app_processor = AppTemplateProcessor()

        self.html_manager = HTMLTemplateManager(self.template_base, self.html_template)
        self.html_processor = HTMLTemplateProcessor()

        self.reporter = Reporter(self)

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'app_name',
            help='The name of the application to create',
            type=str
        )

    def get_app_names(self) -> list[str]:
        from django.apps import apps
        return [config.name for config in apps.get_app_configs()]

    def handle(self, *_args, **kwargs) -> None:
        app = kwargs.get('app_name')

        if not app:
            raise CommandError(self.style.ERROR('The app name is missing'))

        self.app_manager.validate_app_name_format(app)

        components = self.app_manager.parse_app_name(app)
        self.app_manager.is_valid_root_apps(components)

        registered_apps = self.get_app_names()

        self.stdout.write(self.style.NOTICE(f'Checking app components: {components}\n\n'))

        missing_components = self.app_manager.get_missing_components(components, registered_apps)

        if missing_components:
            self.reporter.report_missing_components(missing_components)
            self.reporter.report_app_tree_structure(self.app_base, components, registered_apps, self.app_template)
            self.reporter.report_html_tree_structure(self.template_base, components, registered_apps, self.html_template)

            if not self.reporter.prompt_for_confirmation('\nProceed with app creation? (y/n): '):
                self.stdout.write(self.style.ERROR('App creation aborted.'))
                return

            for module in missing_components:
                self.app_manager.create_custom_app(module, self.app_processor, self.reporter)
                self.html_manager.create_custom_templates(module, self.html_processor, self.reporter)

            self.reporter.report_installed_apps_suggestion(missing_components)
        else:
            self.stdout.write(self.style.SUCCESS('All component(s) exist!'))

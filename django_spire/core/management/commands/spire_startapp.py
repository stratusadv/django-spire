from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand

from django_spire.core.management.commands.spire_startapp_pkg.builder import TemplateBuilder
from django_spire.core.management.commands.spire_startapp_pkg.config import (
    AppConfigFactory,
    PathConfig,
)
from django_spire.core.management.commands.spire_startapp_pkg.filesystem import FileSystem
from django_spire.core.management.commands.spire_startapp_pkg.generator import (
    AppGenerator,
    # TemplateGenerator,
)
from django_spire.core.management.commands.spire_startapp_pkg.processor import (
    TemplateEngine,
    TemplateProcessor,
)
from django_spire.core.management.commands.spire_startapp_pkg.registry import AppRegistry
from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter
from django_spire.core.management.commands.spire_startapp_pkg.resolver import PathResolver
from django_spire.core.management.commands.spire_startapp_pkg.user_input import UserInputCollector
from django_spire.core.management.commands.spire_startapp_pkg.validator import AppValidator

if TYPE_CHECKING:
    from typing import Any


class Command(BaseCommand):
    """
    Django management command for creating custom Spire apps.

    This command guides users through an interactive wizard to create a new Django app
    with a pre-configured structure including models, views, forms, services, and templates.
    It handles nested app structures (e.g., app.parent.child) and validates that all
    parent apps are properly registered before creating child apps.
    """

    help = 'Create a custom Spire app.'

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """
        Main entry point for the management command.

        Orchestrates the entire app creation process by initializing helper classes,
        collecting user input through an interactive wizard, validating the app structure,
        generating app files and templates, and providing feedback to the user.

        :param args: Positional arguments (not used).
        :param kwargs: Keyword arguments (not used).
        """

        filesystem = FileSystem()
        path_config = PathConfig.default()
        path_resolver = PathResolver()
        registry = AppRegistry()
        reporter = Reporter(self)

        template_engine = TemplateEngine()
        template_processor = TemplateProcessor(template_engine, filesystem)

        validator = AppValidator(reporter, registry, path_resolver, filesystem)

        user_input_collector = UserInputCollector(reporter, validator)

        config_factory = AppConfigFactory(path_resolver)

        template_builder = TemplateBuilder(reporter)

        app_generator = AppGenerator(filesystem, template_processor, reporter, path_config)
        # template_generator = TemplateGenerator(filesystem, template_processor, reporter, path_config)

        user_inputs = user_input_collector.collect_all_inputs()
        app_path = user_inputs['app_path']

        validator.validate_app_format(app_path)

        config = config_factory.create_config(app_path, user_inputs)
        validator.validate_root_app(config.components)

        reporter.write(
            f'\nChecking app components: {config.components}\n',
            reporter.style_notice
        )

        missing = registry.get_missing_components(config.components)

        if missing:
            reporter.report_missing_components(missing)

            template_builder.build_app_tree_structure(
                path_resolver.get_base_dir(),
                config.components,
                registry.get_installed_apps(),
                path_config.app_template
            )

            # template_builder.build_html_tree_structure(
            #     path_resolver.get_base_dir(),
            #     config.components,
            #     registry.get_installed_apps(),
            #     path_config.html_template
            # )

            if not reporter.prompt_confirmation('\nProceed with app creation? (y/n): '):
                reporter.write('App creation aborted.', reporter.style_error)
                return

            for module in [missing[-1]]:
                module_config = config_factory.create_config(module, user_inputs)
                app_generator.generate(module_config)
                # template_generator.generate(module_config)

            reporter.report_installed_apps_suggestion(missing)
        else:
            reporter.write('All component(s) exist.', reporter.style_success)

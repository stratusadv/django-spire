from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.management.base import CommandError

if TYPE_CHECKING:
    from pathlib import Path

    from django_spire.core.management.commands.spire_startapp_pkg.config import AppConfig, PathConfig
    from django_spire.core.management.commands.spire_startapp_pkg.filesystem import FileSystemInterface
    from django_spire.core.management.commands.spire_startapp_pkg.processor import TemplateProcessor
    from django_spire.core.management.commands.spire_startapp_pkg.reporter import ReporterInterface


class AppGenerator:
    """
    Generates Django app structures from templates.

    This class handles the creation of new Django apps by copying template
    files and processing them with user-provided configuration.
    """

    def __init__(
        self,
        filesystem: FileSystemInterface,
        processor: TemplateProcessor,
        reporter: ReporterInterface,
        path_config: PathConfig
    ):
        """
        Initializes the AppGenerator with required dependencies.

        :param filesystem: File system interface for file operations.
        :param processor: Template processor for replacing placeholders.
        :param reporter: Reporter for user feedback and output.
        :param path_config: Configuration containing template paths.
        """

        self._filesystem = filesystem
        self._path_config = path_config
        self._processor = processor
        self._reporter = reporter

    def generate(self, config: AppConfig) -> None:
        """
        Generates a new Django app from templates.

        Creates the app directory, copies template files, and processes
        them with user configuration. Skips generation if the app already exists.

        :param config: Configuration for the app to generate.
        """

        if self._filesystem.has_content(config.destination):
            self._reporter.report_app_exists(config.app_path, config.destination)
            return

        self._validate_template_exists(self._path_config.app_template, 'app template')
        self._reporter.report_creating_app(config.app_path, config.destination)

        self._filesystem.create_directory(config.destination)
        self._filesystem.copy_tree(self._path_config.app_template, config.destination)

        self._processor.process_app_templates(
            config.destination,
            config.components,
            config.user_inputs
        )

        self._reporter.report_app_creation_success(config.app_path)

    def _validate_template_exists(self, path: Path, template_type: str) -> None:
        """
        Validates that a template directory exists.

        :param path: Path to the template directory.
        :param template_type: Description of the template type for error messages.
        :raises CommandError: If the template directory does not exist.
        """

        if not self._filesystem.exists(path):
            self._reporter.write('\n', self._reporter.style_notice)

            message = (
                f'Template directory "{path}" is missing. '
                f'Ensure you have a valid {template_type}.'
            )

            raise CommandError(message)


class TemplateGenerator:
    """
    Generates HTML templates for Django apps.

    This class handles the creation of HTML template files including
    forms, cards, pages, and items for new Django apps.
    """

    def __init__(
        self,
        filesystem: FileSystemInterface,
        processor: TemplateProcessor,
        reporter: ReporterInterface,
        path_config: PathConfig
    ):
        """
        Initializes the TemplateGenerator with required dependencies.

        :param filesystem: File system interface for file operations.
        :param processor: Template processor for replacing placeholders.
        :param reporter: Reporter for user feedback and output.
        :param path_config: Configuration containing template paths.
        """

        self._filesystem = filesystem
        self._path_config = path_config
        self._processor = processor
        self._reporter = reporter

    def generate(self, config: AppConfig) -> None:
        """
        Generates HTML templates for a new Django app.

        Creates the template directory, copies template files, and processes
        them with user configuration. Skips generation if templates already exist.

        :param config: Configuration for the templates to generate.
        """

        if self._filesystem.has_content(config.template_destination):
            self._reporter.report_templates_exist(config.app_path, config.template_destination)
            return

        self._validate_template_exists(self._path_config.html_template, 'templates template')
        self._reporter.report_creating_templates(config.app_path, config.template_destination)

        self._filesystem.create_directory(config.template_destination)
        self._filesystem.copy_tree(self._path_config.html_template, config.template_destination)

        self._processor.process_html_templates(
            config.template_destination,
            config.components,
            config.user_inputs
        )

        self._reporter.report_templates_creation_success(config.app_path)

    def _validate_template_exists(self, path: Path, template_type: str) -> None:
        """
        Validates that a template directory exists.

        :param path: Path to the template directory.
        :param template_type: Description of the template type for error messages.
        :raises CommandError: If the template directory does not exist.
        """

        if not self._filesystem.exists(path):
            self._reporter.write('\n', self._reporter.style_notice)

            message = (
                f'Template directory "{path}" is missing. '
                f'Ensure you have a valid {template_type}.'
            )

            raise CommandError(message)

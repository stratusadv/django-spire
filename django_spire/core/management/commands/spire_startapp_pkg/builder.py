from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.management.commands.spire_startapp_pkg.maps import generate_replacement_map

if TYPE_CHECKING:
    from pathlib import Path

    from django_spire.core.management.commands.spire_startapp_pkg.reporter import ReporterInterface


class TemplateBuilder:
    """
    Builds and displays tree structures for app and template creation.

    This class generates visual representations of the file structure
    that will be created for new apps and their associated templates.
    """

    def __init__(self, reporter: ReporterInterface):
        """
        Initializes the TemplateBuilder with a reporter for output.

        :param reporter: Reporter instance for displaying output to the user.
        """

        self._reporter = reporter

    def build_app_tree_structure(
        self,
        base: Path,
        components: list[str],
        registry: list[str],
        template: Path
    ) -> None:
        """
        Displays a tree structure of the app files that will be created.

        This method shows the user what Python files, directories, and modules
        will be generated for the new Django app before creation.

        :param base: Base directory where the app will be created.
        :param components: List of app path components (e.g., ['app', 'human_resource', 'employee']).
        :param registry: List of already registered apps in the Django project.
        :param template: Path to the app template directory.
        """

        self._reporter.report_tree_structure(
            title='\nThe following app(s) will be created:\n\n',
            base=base,
            components=components,
            registry=registry,
            template=template,
            formatter=self._reporter.format_app_item,
            transformation=self._reporter.transform_app_component,
        )

    def build_html_tree_structure(
        self,
        base: Path,
        components: list[str],
        registry: list[str],
        template: Path
    ) -> None:
        """
        Displays a tree structure of the HTML template files that will be created.

        This method shows the user what HTML templates, cards, forms, and pages
        will be generated for the new Django app before creation.

        :param base: Base directory where templates will be created.
        :param components: List of app path components.
        :param registry: List of already registered apps in the Django project.
        :param template: Path to the HTML template directory.
        """

        replacement = generate_replacement_map(components)

        def html_formatter_with_replacement(item: Path) -> str:
            return self._reporter.format_html_item(item, replacement)

        self._reporter.report_tree_structure(
            title='\nThe following template(s) will be created:\n\n',
            base=base,
            components=components,
            registry=registry,
            template=template,
            formatter=html_formatter_with_replacement,
            transformation=self._reporter.transform_html_component,
        )

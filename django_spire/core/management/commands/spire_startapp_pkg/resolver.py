from __future__ import annotations

from pathlib import Path

from django.conf import settings


class PathResolver:
    """
    Resolves file system paths for app and template creation.

    This class determines where new Django apps and their templates
    should be created based on project structure and configuration.
    """

    def __init__(self, base_dir: Path | None = None, template_dir: Path | None = None):
        """
        Initializes the path resolver with base directories.

        :param base_dir: Optional base directory for the Django project (defaults to settings.BASE_DIR).
        :param template_dir: Optional template directory (defaults to base_dir/templates).
        """

        self._base_dir = base_dir or Path(settings.BASE_DIR)
        self._template_dir = template_dir or self._base_dir / 'templates'

    def get_app_destination(self, components: list[str]) -> Path:
        """
        Gets the destination path for a new app based on its components.

        For components ['app', 'human_resource', 'employee'], returns
        Path('base_dir/app/human_resource/employee').

        :param components: List of app path components.
        :return: Full path where the app should be created.
        """

        return self._base_dir.joinpath(*components)

    def get_base_dir(self) -> Path:
        """
        Gets the project's base directory.

        :return: Base directory path for the Django project.
        """

        return self._base_dir

    def get_template_destination(self, components: list[str]) -> Path:
        """
        Gets the destination path for templates based on app components.

        Excludes the first component (root app) from the path. For components
        ['app', 'human_resource', 'employee'], returns
        Path('templates/human_resource/employee').

        :param components: List of app path components.
        :return: Full path where templates should be created.
        """

        template_components = components[1:] if len(components) > 1 else components
        return self._template_dir.joinpath(*template_components)

    def get_template_dir(self) -> Path:
        """
        Gets the project's template directory.

        :return: Template directory path for the Django project.
        """

        return self._template_dir

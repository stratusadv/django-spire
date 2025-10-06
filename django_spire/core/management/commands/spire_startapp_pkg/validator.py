from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.management.base import CommandError

if TYPE_CHECKING:
    from django_spire.core.management.commands.spire_startapp_pkg.filesystem import FileSystemInterface
    from django_spire.core.management.commands.spire_startapp_pkg.registry import AppRegistryInterface
    from django_spire.core.management.commands.spire_startapp_pkg.reporter import ReporterInterface
    from django_spire.core.management.commands.spire_startapp_pkg.resolver import PathResolverInterface


class AppValidator:
    """
    Validates Django app paths and configurations.

    This class performs validation checks to ensure app paths are properly
    formatted, don't conflict with existing apps, and use valid root apps.
    """

    def __init__(
        self,
        reporter: ReporterInterface,
        registry: AppRegistryInterface,
        path_resolver: PathResolverInterface,
        filesystem: FileSystemInterface
    ):
        """
        Initializes the validator with required dependencies.

        :param reporter: Reporter for displaying error messages.
        :param registry: Registry for checking installed apps.
        :param path_resolver: Path resolver for determining file locations.
        :param filesystem: File system interface for checking file existence.
        """

        self._filesystem = filesystem
        self._path_resolver = path_resolver
        self._registry = registry
        self._reporter = reporter

    def validate_app_format(self, app_path: str) -> None:
        """
        Validates that an app path uses dot notation.

        :param app_path: App path to validate.
        :raises CommandError: If the app path doesn't contain dots.
        """

        if '.' not in app_path:
            self._reporter.write('\n', self._reporter.style_notice)

            message = 'Invalid app name format. The app path must use dot notation (e.g., "parent.child").'
            raise CommandError(message)

    def validate_app_path(self, components: list[str]) -> None:
        """
        Validates that an app path doesn't already exist.

        :param components: List of app path components.
        :raises CommandError: If an app already exists at the destination path.
        """

        destination = self._path_resolver.get_app_destination(components)

        if self._filesystem.has_content(destination):
            self._reporter.write('\n', self._reporter.style_notice)

            message = (
                f'The app already exists at {destination}. '
                'Please remove the existing app or choose a different name.'
            )

            raise CommandError(message)

    def validate_root_app(self, components: list[str]) -> None:
        """
        Validates that the root app component is registered in Django.

        :param components: List of app path components.
        :raises CommandError: If the root app is not a valid registered app.
        """

        valid_roots = self._registry.get_valid_root_apps()
        root = components[0]

        if root not in valid_roots:
            self._reporter.write('\n', self._reporter.style_notice)

            message = (
                f'Invalid root app "{root}". '
                f'Valid root apps: {", ".join(sorted(valid_roots))}.'
            )

            raise CommandError(message)

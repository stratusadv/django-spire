from __future__ import annotations

from typing import Protocol

from django.apps import apps
from django.conf import settings


class AppRegistryInterface(Protocol):
    """
    Protocol defining the interface for Django app registry operations.

    This protocol specifies methods for querying registered apps and
    validating app component paths.
    """

    def get_installed_apps(self) -> list[str]: ...
    def get_missing_components(self, components: list[str]) -> list[str]: ...
    def get_valid_root_apps(self) -> set[str]: ...
    def is_app_registered(self, app_path: str) -> bool: ...


class AppRegistry:
    """
    Manages Django app registration information.

    This class provides methods to query which apps are installed in the
    Django project and validate app component hierarchies.
    """

    def get_installed_apps(self) -> list[str]:
        """
        Gets a list of all installed app names.

        :return: List of fully qualified app names from Django's app registry.
        """

        return [config.name for config in apps.get_app_configs()]

    def get_missing_components(self, components: list[str]) -> list[str]:
        """
        Identifies which app components in a path are not registered.

        For a path like ['app', 'human_resource', 'employee'], this checks
        if 'app', 'app.human_resource', and 'app.human_resource.employee'
        are registered, and returns those that are missing.

        :param components: List of app path components to check.
        :return: List of unregistered component paths.
        """

        registry = self.get_installed_apps()
        missing = []

        total = len(components)

        for i in range(total):
            component = '.'.join(components[: i + 1])

            if component not in registry and i > 0:
                missing.append(component)

        return missing

    def get_valid_root_apps(self) -> set[str]:
        """
        Gets all valid root app names from INSTALLED_APPS.

        Returns root-level apps (first component before a dot) that can be
        used as parent apps, excluding Django's built-in apps.

        :return: Set of valid root app names.
        """

        return {
            app.split('.')[0]
            for app in settings.INSTALLED_APPS
            if '.' in app and app.split('.')[0] != 'django'
        }

    def is_app_registered(self, app_path: str) -> bool:
        """
        Checks if an app path is registered in Django.

        :param app_path: Dot-separated app path to check.
        :return: True if the app is registered, False otherwise.
        """

        return app_path in self.get_installed_apps()

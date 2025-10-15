from __future__ import annotations

import django_spire

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.core.management.commands.spire_startapp_pkg.resolver import PathResolverInterface


@dataclass(frozen=True)
class PathConfig:
    """
    Configuration for template directory paths.

    This class holds the paths to the app and HTML template directories
    used for generating new Django apps.
    """

    app_template: Path
    html_template: Path

    @classmethod
    def default(cls) -> PathConfig:
        """
        Creates a default PathConfig with standard template locations.

        :return: PathConfig instance with paths to default app and HTML templates.
        """

        base = Path(django_spire.__file__).parent

        return cls(
            app_template=base / 'core/management/commands/spire_startapp_pkg/template/app',
            html_template=base / 'core/management/commands/spire_startapp_pkg/template/templates'
        )


@dataclass(frozen=True)
class AppConfig:
    """
    Configuration for a new Django app being created.

    This class contains all the information needed to generate a new app,
    including its name, path, components, destinations, and user-provided inputs.
    """

    app_name: str
    app_path: str
    components: list[str]
    destination: Path
    template_destination: Path
    user_inputs: dict[str, str]

    @property
    def app_label(self) -> str:
        """
        Gets the Django app label.

        :return: The app label, either from user input or derived from app name.
        """

        return self.user_inputs.get('app_label', self.app_name.lower())

    @property
    def model_name(self) -> str:
        """
        Gets the model class name.

        :return: The model name, either from user input or TitleCase version of app name.
        """

        default = ''.join(word.title() for word in self.app_name.split('_'))
        return self.user_inputs.get('model_name', default)


class AppConfigFactory:
    """
    Factory class for creating AppConfig instances.

    This class handles the creation of AppConfig objects by resolving
    paths and processing user inputs.
    """

    def __init__(self, path_resolver: PathResolverInterface):
        """
        Initializes the factory with a path resolver.

        :param path_resolver: Path resolver for determining file system locations.
        """

        self._path_resolver = path_resolver

    def create_config(self, app_path: str, user_inputs: dict[str, str]) -> AppConfig:
        """
        Creates an AppConfig from an app path and user inputs.

        :param app_path: Dot-separated app path (e.g., 'app.human_resource.employee').
        :param user_inputs: Dictionary of user-provided configuration values.
        :return: Configured AppConfig instance ready for app generation.
        """

        components = app_path.split('.')
        app_name = user_inputs.get('app_name', components[-1])

        return AppConfig(
            app_name=app_name,
            app_path=app_path,
            components=components,
            destination=self._path_resolver.get_app_destination(components),
            template_destination=self._path_resolver.get_template_destination(components),
            user_inputs=user_inputs
        )

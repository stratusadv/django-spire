from __future__ import annotations

from django_spire.core.management.commands.spire_startapp_pkg.builder import TemplateBuilder
from django_spire.core.management.commands.spire_startapp_pkg.config import (
    AppConfig,
    AppConfigFactory,
    PathConfig,
)
from django_spire.core.management.commands.spire_startapp_pkg.filesystem import (
    FileSystem,
    FileSystemInterface,
)
from django_spire.core.management.commands.spire_startapp_pkg.generator import (
    AppGenerator,
    TemplateGenerator,
)
from django_spire.core.management.commands.spire_startapp_pkg.maps import generate_replacement_map
from django_spire.core.management.commands.spire_startapp_pkg.permissions import PermissionInheritanceHandler
from django_spire.core.management.commands.spire_startapp_pkg.processor import (
    TemplateEngine,
    TemplateProcessor,
)
from django_spire.core.management.commands.spire_startapp_pkg.registry import (
    AppRegistry,
    AppRegistryInterface,
)
from django_spire.core.management.commands.spire_startapp_pkg.reporter import (
    Reporter,
    ReporterInterface,
)
from django_spire.core.management.commands.spire_startapp_pkg.resolver import (
    PathResolver,
    PathResolverInterface,
)
from django_spire.core.management.commands.spire_startapp_pkg.user_input import UserInputCollector
from django_spire.core.management.commands.spire_startapp_pkg.validator import AppValidator


__all__ = [
    'AppConfig',
    'AppConfigFactory',
    'AppGenerator',
    'AppRegistry',
    'AppRegistryInterface',
    'AppValidator',
    'FileSystem',
    'FileSystemInterface',
    'PathConfig',
    'PathResolver',
    'PathResolverInterface',
    'PermissionInheritanceHandler',
    'Reporter',
    'ReporterInterface',
    'TemplateBuilder',
    'TemplateEngine',
    'TemplateGenerator',
    'TemplateProcessor',
    'UserInputCollector',
    'generate_replacement_map',
]

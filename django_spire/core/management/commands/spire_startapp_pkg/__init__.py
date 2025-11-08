from __future__ import annotations

from django_spire.core.management.commands.spire_startapp_pkg.builder import TemplateBuilder
from django_spire.core.management.commands.spire_startapp_pkg.config import (
    AppConfig,
    AppConfigFactory,
    PathConfig,
)
from django_spire.core.management.commands.spire_startapp_pkg.filesystem import FileSystem
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
from django_spire.core.management.commands.spire_startapp_pkg.registry import AppRegistry
from django_spire.core.management.commands.spire_startapp_pkg.reporter import Reporter
from django_spire.core.management.commands.spire_startapp_pkg.resolver import PathResolver
from django_spire.core.management.commands.spire_startapp_pkg.user_input import UserInputCollector
from django_spire.core.management.commands.spire_startapp_pkg.validator import AppValidator


__all__ = [
    'AppConfig',
    'AppConfigFactory',
    'AppGenerator',
    'AppRegistry',
    'AppValidator',
    'FileSystem',
    'PathConfig',
    'PathResolver',
    'PermissionInheritanceHandler',
    'Reporter',
    'TemplateBuilder',
    'TemplateEngine',
    'TemplateGenerator',
    'TemplateProcessor',
    'UserInputCollector',
    'generate_replacement_map',
]

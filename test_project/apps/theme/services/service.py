from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from test_project.apps.theme.services.factory_service import ThemeFactoryService
from test_project.apps.theme.services.processor_service import ThemeProcessorService
from test_project.apps.theme.services.intelligence_service import ThemeIntelligenceService


if TYPE_CHECKING:
    from test_project.apps.theme.models import Theme


class ThemeService(BaseDjangoModelService['Theme']):
    obj: Theme

    intelligence = ThemeIntelligenceService()
    processor = ThemeProcessorService()
    factory = ThemeFactoryService()
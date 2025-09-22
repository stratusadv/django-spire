from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from module.services.factory_service import SpireChildAppFactoryService
from module.services.processor_service import SpireChildAppProcessorService
from module.services.intelligence_service import SpireChildAppIntelligenceService
from module.services.transformation_service import SpireChildAppTransformationService

if TYPE_CHECKING:
    from module.models import SpireChildApp


class SpireChildAppService(BaseDjangoModelService['SpireChildApp']):
    obj: SpireChildApp

    intelligence = SpireChildAppIntelligenceService()
    processor = SpireChildAppProcessorService()
    factory = SpireChildAppFactoryService()
    transformation = SpireChildAppTransformationService()

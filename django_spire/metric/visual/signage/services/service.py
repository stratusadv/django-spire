from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from django_spire.metric.visual.signage.services.factory_service import SignageFactoryService
from django_spire.metric.visual.signage.services.intelligence_service import SignageIntelligenceService
from django_spire.metric.visual.signage.services.processor_service import SignageProcessorService
from django_spire.metric.visual.signage.services.transformation_service import SignageTransformationService

if TYPE_CHECKING:
    from django_spire.metric.visual.signage.models import Signage


class SignageService(BaseDjangoModelService['Signage']):
    obj: Signage

    intelligence = SignageIntelligenceService()
    processor = SignageProcessorService()
    factory = SignageFactoryService()
    transformation = SignageTransformationService()

from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from django_spire.metric.visual.services.factory_service import VisualFactoryService
from django_spire.metric.visual.services.intelligence_service import VisualIntelligenceService
from django_spire.metric.visual.services.processor_service import VisualProcessorService
from django_spire.metric.visual.services.transformation_service import VisualTransformationService

if TYPE_CHECKING:
    from django_spire.metric.visual.models import Visual


class VisualService(BaseDjangoModelService['Visual']):
    obj: Visual

    intelligence = VisualIntelligenceService()
    processor = VisualProcessorService()
    factory = VisualFactoryService()
    transformation = VisualTransformationService()

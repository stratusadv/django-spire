from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from django_spire.metric.domain.services.factory_service import DomainFactoryService
from django_spire.metric.domain.services.intelligence_service import DomainIntelligenceService
from django_spire.metric.domain.services.processor_service import DomainProcessorService
from django_spire.metric.domain.services.transformation_service import DomainTransformationService

if TYPE_CHECKING:
    from django_spire.metric.domain.models import Domain


class DomainService(BaseDjangoModelService['Domain']):
    obj: Domain

    intelligence = DomainIntelligenceService()
    processor = DomainProcessorService()
    factory = DomainFactoryService()
    transformation = DomainTransformationService()

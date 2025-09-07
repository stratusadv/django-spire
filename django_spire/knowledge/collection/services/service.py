from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.collection.services.ordering_service import \
    CollectionOrderingService
from django_spire.knowledge.collection.services.processor_service import \
    CollectionProcessorService
from django_spire.knowledge.collection.services.transformation_service import \
    CollectionTransformationService

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionService(BaseDjangoModelService['Collection']):
    obj: Collection

    ordering: CollectionOrderingService = CollectionOrderingService()
    processor: CollectionProcessorService = CollectionProcessorService()
    transformation: CollectionTransformationService = CollectionTransformationService()


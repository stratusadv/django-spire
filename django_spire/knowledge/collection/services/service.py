from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.collection.services.transformation_service import \
    CollectionTransformationService

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionService(BaseDjangoModelService['Collection']):
    obj: Collection

    transformation: CollectionTransformationService = CollectionTransformationService()

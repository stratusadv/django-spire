from __future__ import annotations

from django_spire.contrib.ordering.service import OrderingService
from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionService(BaseDjangoModelService['Collection']):
    obj: Collection

    ordering: OrderingService = OrderingService()

from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.ordering.services.processor_service import OrderingProcessorService
from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.contrib.ordering.mixins import OrderingModelMixin


class OrderingService(BaseDjangoModelService['OrderingModelMixin']):
    obj: OrderingModelMixin

    processor = OrderingProcessorService()

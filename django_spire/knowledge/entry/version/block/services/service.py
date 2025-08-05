from __future__ import annotations

from django_spire.contrib.ordering.service import OrderingService
from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING, Any

from django_spire.knowledge.entry.version.block.services.factory_service import \
    EntryVersionBlockFactoryService
from django_spire.knowledge.entry.version.block.services.processor_service import \
    EntryVersionBlockProcessorService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    factory: EntryVersionBlockFactoryService = EntryVersionBlockFactoryService()
    ordering: OrderingService = OrderingService()
    processor: EntryVersionBlockProcessorService = EntryVersionBlockProcessorService()

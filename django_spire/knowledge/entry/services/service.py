from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.ordering.service import OrderingService
from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.services.processor_service import EntryVersionProcessorService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry, EntryVersion


class EntryService(BaseDjangoModelService[Entry]):
    obj: Entry

    ordering: OrderingService = OrderingService()


class EntryVersionService(BaseDjangoModelService[EntryVersion]):
    obj: EntryVersion

    processor: EntryVersionProcessorService = EntryVersionProcessorService()

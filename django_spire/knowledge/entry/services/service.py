from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.services.processor import EntryVersionProcessorService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import EntryVersion


class EntryVersionService(BaseDjangoModelService['EntryVersion']):
    obj: EntryVersion

    processor: EntryVersionProcessorService = EntryVersionProcessorService()

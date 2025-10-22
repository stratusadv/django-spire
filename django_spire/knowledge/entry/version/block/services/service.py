from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.entry.version.block.services.factory_service import \
    EntryVersionBlockFactoryService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    factory = EntryVersionBlockFactoryService()

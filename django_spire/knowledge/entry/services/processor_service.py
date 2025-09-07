from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class EntryProcessorService(BaseDjangoModelService['Entry']):
    obj: Entry

    def set_deleted(self):
        self.obj.ordering_services.processor.remove_from_objects(
            destination_objects=self.obj.collection.entries.active()
        )
        self.obj.set_deleted()

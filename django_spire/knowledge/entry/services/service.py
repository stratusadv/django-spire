from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.ordering.service import OrderingService
from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.services.processor_service import EntryVersionProcessorService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry, EntryVersion


class EntryService(BaseDjangoModelService['Entry']):
    obj: Entry

    ordering: OrderingService = OrderingService()

    def save_model_obj(self, author: AuthUser, **field_data) -> bool:
        created = super().save_model_obj(**field_data)

        if created:
            from django_spire.knowledge.entry.models import EntryVersion

            entry_version = EntryVersion.objects.create(
                entry=self.obj,
                author=author
            )

            self.obj.current_version = entry_version
            self.obj.save()

        return created


class EntryVersionService(BaseDjangoModelService['EntryVersion']):
    obj: EntryVersion

    processor: EntryVersionProcessorService = EntryVersionProcessorService()

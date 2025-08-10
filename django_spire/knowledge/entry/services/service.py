from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.ordering.service import OrderingService
from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.services.factory_service import EntryFactoryService
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class EntryService(BaseDjangoModelService['Entry']):
    obj: Entry

    factory: EntryFactoryService = EntryFactoryService()
    ordering: OrderingService = OrderingService()

    def save_model_obj(self, author: AuthUser, **field_data) -> tuple[Entry, bool]:
        self.obj, created = super().save_model_obj(**field_data)

        if created:
            entry_version, _ = EntryVersion.services.save_model_obj(
                entry=self.obj,
                author=author
            )

            self.obj.current_version = entry_version
            self.obj.save()

        return self.obj, created

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import F

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import EntryVersion
    from django_spire.knowledge.entry.block.models import EntryVersionBlock


class EntryVersionProcessorService(BaseDjangoModelService['EntryVersion']):
    obj: EntryVersion

    def insert_block(self, version_block: EntryVersionBlock):
        self.obj_class.objects.greater_or_equal_order(
            version_block=version_block
        ).update(order=F('order') + 1)

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import F
from django.utils.timezone import localtime

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.version.choices import EntryVersionTypeChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
    from django_spire.knowledge.entry.version.models import EntryVersion


class EntryVersionProcessorService(BaseDjangoModelService['EntryVersion']):
    obj: EntryVersion

    def delete_block(self, version_block: EntryVersionBlock):
        version_block.set_deleted()
        (
            self.obj.blocks
            .greater_or_equal_order(order=version_block.order)
            .active()
            .update(order=F('order') - 1)
        )

    def insert_block(self, version_block: EntryVersionBlock):
        (
            self.obj.blocks
            .greater_or_equal_order(order=version_block.order)
            .exclude(pk=version_block.pk)
            .active()
            .update(order=F('order') + 1)
        )

    def publish(self):
        self.obj.status = EntryVersionTypeChoices.PUBLISHED
        self.obj.published_datetime = localtime()
        self.obj.save()

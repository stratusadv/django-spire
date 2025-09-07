from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.timezone import localtime

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.models import EntryVersion


class EntryVersionProcessorService(BaseDjangoModelService['EntryVersion']):
    obj: EntryVersion

    def publish(self):
        self.obj.status = EntryVersionStatusChoices.PUBLISHED
        self.obj.published_datetime = localtime()
        self.obj.save()

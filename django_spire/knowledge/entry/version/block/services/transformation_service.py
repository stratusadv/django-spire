from __future__ import annotations

from django.template.loader import render_to_string

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class EntryVersionBlockTransformationService(BaseDjangoModelService['EntryVersionBlock']):
    obj: EntryVersionBlock

    def to_dict(self) -> dict:
        return {
            'id': self.obj.id,
            'type': self.obj.type,
            'order': self.obj.order,
            'block': self.obj.block.to_dict(self.obj)
        }

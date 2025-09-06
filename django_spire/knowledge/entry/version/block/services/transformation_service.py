from __future__ import annotations

import json

from django.db.models import QuerySet
from django.template.loader import render_to_string

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING, Iterable

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

    def to_json(self) -> str:
        return json.dumps(self.obj.services.transformation.to_dict())

    @staticmethod
    def objects_to_json(objects: Iterable[EntryVersionBlock]) -> str:
        return json.dumps([
            block.services.transformation.to_dict()
            for block in objects
        ])

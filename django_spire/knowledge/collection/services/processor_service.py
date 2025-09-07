from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.core.shortcuts import get_object_or_null_obj

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionProcessorService(BaseDjangoModelService['Collection']):
    obj: Collection

    def set_parent(self, parent_pk: int):
        new_parent = get_object_or_null_obj(self.obj_class, pk=parent_pk)

        self.obj.parent  = None if new_parent.id is None else new_parent
        self.obj.save()


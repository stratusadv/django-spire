from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionProcessorService(BaseDjangoModelService['Collection']):
    obj: Collection

    def set_deleted(self):
        if self.obj.parent_id is None:
            destination_objects = self.obj_class.objects.parentless().active()
        else:
            destination_objects = (
                self.obj_class.objects
                .by_parent_id(parent_id=self.obj.parent_id)
                .active()
            )

        self.obj.ordering_services.processor.remove_from_objects(
            destination_objects=destination_objects
        )
        self.obj.set_deleted()

        for child in self.obj.children.active():
            child.services.processor.set_deleted()

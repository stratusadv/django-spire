from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionOrderingService(BaseDjangoModelService['Collection']):
    obj: Collection

    def reorder(self, order: int, new_parent_pk: int):
        current_parent = self.obj.parent
        if current_parent is None:
            origin_objects = self.obj_class.objects.parentless().active()

        else:
            origin_objects = self.obj_class.objects.by_parent(parent=self.obj.parent).active()

        if new_parent_pk == -1:
            destination_objects = self.obj_class.objects.parentless().active()

        else:
            new_parent = self.obj_class.objects.get(pk=new_parent_pk)
            destination_objects = new_parent.children.active()

        self.obj.ordering_services.processor.move_to_position(
            destination_objects=destination_objects,
            position=order,
            origin_objects=origin_objects
        )
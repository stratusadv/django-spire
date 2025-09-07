from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

from django_spire.knowledge.collection.services.ordering_service import \
    CollectionOrderingService
from django_spire.knowledge.collection.services.processor_service import \
    CollectionProcessorService
from django_spire.knowledge.collection.services.transformation_service import \
    CollectionTransformationService

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionService(BaseDjangoModelService['Collection']):
    obj: Collection

    ordering = CollectionOrderingService()
    processor = CollectionProcessorService()
    transformation = CollectionTransformationService()

    def save_model_obj(self, **field_data) -> tuple[Collection, bool]:
        self.obj, created = super().save_model_obj(**field_data)

        if self.obj.parent_id is None:
            destination_objects = self.obj_class.objects.parentless().active()
        else:
            destination_objects = (
                self.obj_class.objects
                .by_parent_id(parent_id=self.obj.parent_id)
                .active()
            )

        self.obj.ordering_services.processor.move_to_position(
            destination_objects=destination_objects,
            position=0 if created else self.obj.order,
        )

        return self.obj, created

from __future__ import annotations

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionToolService(BaseDjangoModelService['Collection']):
    obj: Collection

    def get_children_ids(self, parent_id: int) -> set[int]:
        descendant_ids = set()
        current_level_ids = [parent_id]

        while current_level_ids:
            child_ids = self.obj_class.objects.by_parent_ids(
                parent_ids=current_level_ids
            ).values_list('id', flat=True)

            if not child_ids:
                break

            descendant_ids.update(child_ids)
            current_level_ids = child_ids

        return descendant_ids

    def get_root_collection_pk(self) -> int:
        collection = self.obj

        while collection.parent_id:
            collection = collection.parent

        return collection.id

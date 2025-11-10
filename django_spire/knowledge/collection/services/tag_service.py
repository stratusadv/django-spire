from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionTagService(BaseDjangoModelService['Collection']):
    obj: Collection

    def update_parent_aggregated_tags(self, tag_set: set[str] | None = None):
        if self.obj.parent:
            self.obj.parent.services.tag.update_parent_aggregated_tags(
                self.obj.get_and_set_aggregated_tag_set(tag_set=tag_set)
            )




from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt

from django_spire.core.tag.intelligence.tag_set_bot import TagSetBot
from django_spire.core.tag.service.tag_service import BaseTagService
from django_spire.core.tag.tools import (
    get_score_percentage_from_tag_set_weighted,
    simplify_and_weight_tag_set_to_dict,
    simplify_tag_set
)

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionTagService(BaseTagService['Collection']):
    obj: Collection

    def process_and_set_tags(self):
        collection_prompt = Prompt()

        collection_prompt.sub_heading(self.obj.name)
        collection_prompt.text(self.obj.description)

        tag_set = TagSetBot().process(
            content=collection_prompt
        )

        self.set_tags_from_tag_set(
            tag_set=tag_set,
        )

    def get_aggregated_tag_set(self) -> set[str]:
        tag_set = self.obj.tag_set

        for collection in self.obj.children.active():
            tag_set.update(collection.services.tag.get_aggregated_tag_set())

        for entry in self.obj.entries.active():
            tag_set.update(entry.tag_set)

        return tag_set

    def get_score_percentage_from_aggregated_tag_set_weighted(self, tag_set: set[str]) -> float:
        return get_score_percentage_from_tag_set_weighted(
            tag_set_actual=tag_set,
            tag_set_reference=self.get_aggregated_tag_set()
        )

    def get_simplified_aggregated_tag_set(self) -> set[str]:
        return simplify_tag_set(self.get_aggregated_tag_set())

    def get_simplified_and_weighted_aggregated_tag_set(self) -> dict[str, int]:
        return simplify_and_weight_tag_set_to_dict(self.get_aggregated_tag_set())

from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.core.tags.intelligence.tag_set_bot import TagSetBot

if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionTagService(BaseDjangoModelService['Collection']):
    obj: Collection

    def process_and_set_tags(self):
        collection_prompt = Prompt()

        collection_prompt.sub_heading(self.obj.name)
        collection_prompt.text(self.obj.description)

        tag_set = TagSetBot().process(
            content=collection_prompt
        )

        self.obj.set_tags_from_tag_set(
            tag_set=tag_set,
        )

    def get_aggregated_tag_set(self):
        tag_set = self.obj.tag_set

        for collection in self.obj.children.active():
            tag_set.update(collection.services.tag.get_aggregated_tag_set())

        for entry in self.obj.entries.active():
            tag_set.update(entry.tag_set)

        return tag_set

    def get_aggregated_tag_set_simplified(self):
        tag_set = self.obj.tag_set_simplified

        for collection in self.obj.children.active():
            tag_set.update(collection.services.tag.get_aggregated_tag_set())

        for entry in self.obj.entries.active():
            tag_set.update(entry.tag_set_simplified)

        return tag_set


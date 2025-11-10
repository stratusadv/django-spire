from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.core.tags.intelligence.tag_set_bot import TagSetBot

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry



class EntryTagService(BaseDjangoModelService['Entry']):
    obj: Entry

    def update_parent_aggregated_tags(self, tag_set: set[str] | None = None):
        if self.obj.collection:
            self.obj.collection.services.tag.update_parent_aggregated_tags(
                self.obj.get_and_set_aggregated_tag_set(tag_set=tag_set)
            )

    def process_and_set_tags(self):
        entry_prompt = Prompt()

        entry_prompt.text(self.obj.name)

        for version_block in self.obj.current_version.blocks.all():
            entry_prompt.text(f'{version_block.render_to_text()}')

        tag_set = TagSetBot().process(
            content=entry_prompt
        )

        print(tag_set)

        self.obj.set_tags_from_tag_set(
            tag_set=tag_set,
            also_set_aggregated=True
        )



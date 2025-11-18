from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt

from django_spire.core.tag.intelligence.tag_set_bot import TagSetBot
from django_spire.core.tag.service.tag_service import BaseTagService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry



class EntryTagService(BaseTagService['Entry']):
    obj: Entry

    def process_and_set_tags(self):
        entry_prompt = Prompt()

        entry_prompt.sub_heading(self.obj.name)

        for version_block in self.obj.current_version.blocks.all():
            entry_prompt.text(f'{version_block.render_to_text()}')

        tag_set = TagSetBot().process(
            content=entry_prompt
        )

        self.set_tags_from_tag_set(
            tag_set=tag_set,
        )



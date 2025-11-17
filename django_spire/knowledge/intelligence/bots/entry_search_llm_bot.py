from __future__ import annotations

from dandy import Bot, Prompt

from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.intelligence.intel.collection_intel import CollectionIntel
from django_spire.knowledge.intelligence.intel.entry_intel import EntryIntel


class EntrySearchBot(Bot):
    llm_role = 'Knowledge Entry Search Assistant'
    llm_task = 'Read through the knowledge entry the information request and return information and the block id that relevant'
    llm_guidelines = (
        Prompt()
        .list([
            'Make sure the relevant heading text is from a heading with mark down formatting.'
            'When returning the relevant heading remove any of the markdown formating characters.'
        ])
    )
    llm_intel_class = EntryIntel

    def process(self, user_input: str, entry: Entry) -> EntryIntel:
        entry_prompt = Prompt()
        entry_prompt.sub_heading('Information Request')
        entry_prompt.line_break()
        entry_prompt.text(f'{user_input}')
        entry_prompt.line_break()
        entry_prompt.sub_heading('Knowledge Entry')
        entry_prompt.line_break()
        entry_prompt.text(f'0: # {entry.name}')
        entry_prompt.line_break()

        for version_block in entry.current_version.blocks.all():
            entry_prompt.text(f'{version_block.id}: {version_block.render_to_text()}')

        entry_intel = self.llm.prompt_to_intel(
            prompt=entry_prompt,
            exclude_fields={'entry_id', 'collection_intel'},
        )

        entry_intel.entry_id = entry.id
        entry_intel.collection_intel = CollectionIntel(
            name=entry.collection.name,
            collection_id=entry.collection.id,
        )

        return entry_intel

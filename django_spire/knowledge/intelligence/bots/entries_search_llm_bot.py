from __future__ import annotations
from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class EntriesSearchBot(Bot):
    llm_role = 'Knowledge Entry Search Assistant'
    llm_task = 'Read through the knowledge and return information and the block id that relevant to the information request.'
    llm_guidelines = (
        Prompt()
        .list([
            'Please read through all the blocks and return 2 of the most relevant ones.',
            'You can add any of the text in the knowledge entries to the 2 responses if it helps.',
            'Make sure the relevant heading text is from a heading with mark down formatting.',
            'When returning the relevant heading remove any of the markdown formating characters.',
        ])
    )
    llm_intel_class = EntriesIntel

    def process(self, user_input: str, entries: list[Entry]) -> EntriesIntel:

        entry_prompt = Prompt()
        entry_prompt.sub_heading('Information Request')
        entry_prompt.line_break()
        entry_prompt.text(f'{user_input}')
        entry_prompt.line_break()
        entry_prompt.sub_heading('Knowledge Entries')
        entry_prompt.line_break()

        for entry in entries:
            for version_block in entry.current_version.blocks.all():
                if version_block.render_to_text() != '\n':
                    entry_prompt.text(f'{version_block.id}: {version_block.render_to_text()}')

        return self.llm.prompt_to_intel(
            prompt=entry_prompt,
        )


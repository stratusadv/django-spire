from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class KnowledgeEntriesBot(Bot):
    role = 'Knowledge Entry Search Assistant'
    task = 'Read through the knowledge entries and return the most relevant for the user request.'
    guidelines = (
        Prompt()
        .list([
            'Return 1 to 5 of the most relevant knowledge entries using block ids.',
            'The relevant headings should be the nearest heading above the selected knowledge entry block.',
            'Make sure the relevant heading text is from a heading with mark down formatting.',
            'When returning the relevant heading remove any of the markdown formating characters.',
        ])
    )
    intel_class = EntriesIntel

    def process(self, user_input: str, entries: list[Entry]) -> EntriesIntel:
        entry_prompt = Prompt()
        entry_prompt.sub_heading('User Request')
        entry_prompt.line_break()
        entry_prompt.text(f'{user_input}')
        entry_prompt.line_break()
        entry_prompt.sub_heading('Knowledge Entries')
        entry_prompt.line_break()

        for entry in entries:
            entry_prompt.text(f'Entry: {entry.name}')

            for version_block in entry.current_version.blocks.all():
                if version_block.render_to_text() != '\n':
                    entry_prompt.text(f'{version_block.id}: {version_block.render_to_text()}')

            entry_prompt.line_break()

        return self.llm.prompt_to_intel(
            prompt=entry_prompt,
        )

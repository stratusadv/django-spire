from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from django_spire.knowledge.intelligence.intel.answer_intel import AnswerIntel

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class KnowledgeAnswerBot(Bot):
    llm_role = 'Knowledge Entry Search Assistant'
    llm_task = 'Read through the knowledge and answer the users request.'
    llm_guidelines = (
        Prompt()
        .list([
            'Make sure the answer is relevant and reflects knowledge entries.',
            'Do not make up information use the provided knowledge entries as a source of truth.',
            'Use line breaks to separate sections of the answer and use 2 if you need to separate the section from the previous.'
        ])
    )
    llm_intel_class = AnswerIntel

    def process(self, user_input: str, entries: list[Entry]) -> AnswerIntel:

        entry_prompt = Prompt()
        entry_prompt.sub_heading('User Request')
        entry_prompt.line_break()
        entry_prompt.text(f'{user_input}')
        entry_prompt.line_break()
        entry_prompt.sub_heading('Knowledge')
        entry_prompt.line_break()

        for entry in entries:
            for version_block in entry.current_version.blocks.all():
                if version_block.render_to_text() != '\n':
                    entry_prompt.text(f'{version_block.render_to_text()}')

        return self.llm.prompt_to_intel(
            prompt=entry_prompt,
        )


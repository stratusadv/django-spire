from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from django_spire.knowledge.intelligence.intel.knowledge_answer_intel import KnowledgeAnswerIntel

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class KnowledgeSearchBot(Bot):
    llm_role = 'Knowledge Entry Search Assistant'
    llm_task = 'Read through the knowledge and return an answer and the block ids.'
    llm_guidelines = (
        Prompt()
        .list([
            'Make sure the answer is relevant and reflects knowledge entries.',
            'Do not make up information use the provided knowledge entries as a source of truth.',
            'Also return 1 to 4 of the most relevant knowledge entries.',
            'Make sure the relevant heading text is from a heading with mark down formatting.',
            'When returning the relevant heading remove any of the markdown formating characters.',
        ])
    )
    llm_intel_class = KnowledgeAnswerIntel

    def process(self, user_input: str, entries: list[Entry]) -> KnowledgeAnswerIntel:

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


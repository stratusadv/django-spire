from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from django_spire.knowledge.intelligence.intel.answer_intel import AnswerIntel

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory

    from django_spire.knowledge.entry.models import Entry


class BlockType(StrEnum):
    HEADING = 'HEADING'
    SUBHEADING = 'SUBHEADING'


class MarkerType(StrEnum):
    ARTICLE = 'ARTICLE'
    END_ARTICLE = 'END ARTICLE'


def format_marker(marker: MarkerType, label: str | None = None) -> str:
    if label:
        return f'[{marker}: {label}]'

    return f'[{marker}]'


class KnowledgeAnswerBot(Bot):
    role = 'Knowledge Entry Search Assistant'
    task = 'Read through the knowledge and answer the users request.'
    guidelines = (
        Prompt()
        .list([
            'Make sure the answer is relevant and reflects knowledge entries.',
            'Do not make up information use the provided knowledge entries as a source of truth.',
            'Use line breaks to separate sections of the answer and use 2 if you need to separate the section from the previous.',
            'Use the conversation history to understand context and references like "before that", "my last query", etc.',
            'When a user asks about an article or section by title, summarize the content of that article or section.',
            f'Content under a [{BlockType.HEADING}] or [{BlockType.SUBHEADING}] belongs to that section.',
        ])
    )
    intel_class = AnswerIntel

    def process(
        self,
        user_input: str,
        entries: list[Entry],
        message_history: MessageHistory | None = None
    ) -> AnswerIntel:
        entry_prompt = Prompt()
        entry_prompt.sub_heading('User Request')
        entry_prompt.line_break()
        entry_prompt.text(f'{user_input}')
        entry_prompt.line_break()
        entry_prompt.sub_heading('Knowledge')
        entry_prompt.line_break()

        for entry in entries:
            entry_prompt.text(format_marker(MarkerType.ARTICLE, entry.name))

            for version_block in entry.current_version.blocks.all():
                text = version_block.render_to_text()

                if text and text != '\n':
                    entry_prompt.text(f'[{version_block.type.upper()}] {text}')

            entry_prompt.text(format_marker(MarkerType.END_ARTICLE))
            entry_prompt.line_break()

        return self.llm.prompt_to_intel(
            prompt=entry_prompt,
            message_history=message_history,
        )

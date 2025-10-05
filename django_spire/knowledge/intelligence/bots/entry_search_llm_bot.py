from __future__ import annotations

from dandy import Bot, Prompt

from django_spire.knowledge.entry.models import Entry


class EntrySearchLlmBot(Bot):
    @classmethod
    def process(cls, user_input: str, entry: Entry) -> str:
        entry_prompt = Prompt()
        entry_prompt.text('You are a helpful assistant that helps users find information about entries.')
        entry_prompt.text(f'User Input: {user_input}')
        entry_prompt.text(f'Entry: {entry.name}')

        for version_block in entry.current_version.blocks.all():
            entry_prompt.text(version_block.render_to_text())

        return cls().llm.prompt_to_text(prompt=entry_prompt)

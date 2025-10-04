from __future__ import annotations

from dandy import Bot, Prompt


class MarkdownFormatLlmBot(Bot):
    @classmethod
    def process(cls, markdown_content: str) -> str:
        markdown_prompt = Prompt()
        markdown_prompt.text(
            'Can you improve the markdown formatting? Do NOT add or change any of the '
            'content.'
        )
        markdown_prompt.text(markdown_content)

        return cls().llm.prompt_to_text(prompt=markdown_prompt)

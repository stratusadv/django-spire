from __future__ import annotations

from dandy import BaseIntel, Bot, Prompt, recorder_to_html_file


class MarkdownTextIntel(BaseIntel):
    text: str


class MarkdownFormatLlmBot(Bot):
    llm_intel_class = MarkdownTextIntel

    @recorder_to_html_file('knowledge_markdown_improvement')
    def process(self, markdown_content: str) -> str:
        markdown_prompt = Prompt()
        markdown_prompt.text(
            'Can you improve the markdown formatting? Do NOT add or change any of the '
            'content.'
        )
        markdown_prompt.line_break()
        markdown_prompt.text(markdown_content)

        result = self.llm.prompt_to_intel(prompt=markdown_prompt)
        return result.text

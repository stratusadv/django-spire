from __future__ import annotations

from dandy import BaseIntel, Bot, Prompt, recorder_to_html_file


class MarkdownIntel(BaseIntel):
    markdown_content: str


class MarkdownFormatLlmBot(Bot):
    llm_role = 'Markdown Formater'
    llm_task = 'Improve the markdown formatting of the content provided to make more logical sense.'
    llm_guidelines = (
        Prompt()
        .list([
            'Make sure the relevant heading text is from a heading with mark down formatting.'
            'Do not change any of the content only change the formatting as needed.'
        ])
    )
    llm_intel_class = MarkdownIntel

    @recorder_to_html_file('knowledge_markdown_improvement')
    def process(self, markdown_content: str) -> str:
        markdown_intel = self.llm.prompt_to_intel(prompt=markdown_content)

        return markdown_intel.markdown_content

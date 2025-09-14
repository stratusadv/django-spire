from dandy.llm import BaseLlmBot, Prompt


class MarkdownFormatLlmBot(BaseLlmBot):

    @classmethod
    def process(
            cls,
            markdown_content: str
    ) -> str:
        markdown_prompt = Prompt()
        markdown_prompt.text(
            'Can you improve the markdown formatting? Do NOT add or change any of the '
            'content.'
        )
        markdown_prompt.line_break()
        markdown_prompt.text(markdown_content)

        return cls.process_prompt_to_intel(prompt=markdown_prompt).text

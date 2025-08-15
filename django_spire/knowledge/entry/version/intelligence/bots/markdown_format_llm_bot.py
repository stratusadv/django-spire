from dandy.llm import BaseLlmBot, LlmConfigOptions


class MarkdownFormatLlmBot(BaseLlmBot):
    config = 'KNOWLEDGE_LLM_BOT'

    @classmethod
    def process(
            cls,
            markdown_content: str
    ) -> str:

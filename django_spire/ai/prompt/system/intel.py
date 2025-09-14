from __future__ import annotations

from dandy.intel import BaseIntel

from django_spire.ai.prompt.bots import DandyPythonPromptBot, TextToMarkdownPromptBot
from django_spire.knowledge.entry.version.intelligence.bots.markdown_format_llm_bot import MarkdownFormatLlmBot


class SystemPromptResultIntel(BaseIntel):
    result: str


class SystemPromptIntel(BaseIntel):
    role: str
    task: str
    guidelines: str
    output_format: str

    def to_markdown(self):
        return TextToMarkdownPromptBot.process(self.to_string())

    def to_python(self):
        return DandyPythonPromptBot.process(self.to_string())

    def to_string(self):
        return (
            f"Role: {self.role}\n"
            f"Task: {self.task}\n"
            f"Guidelines: {self.guidelines}\n"
            f"Output Format: {self.output_format}"
        )

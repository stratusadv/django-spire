from __future__ import annotations

from dandy import Bot

from django_spire.ai.prompt import prompts
from django_spire.ai.prompt import intel


class DandyPythonPromptBot(Bot):
    llm_role = prompts.dandy_prompt_python_file_instruction_bot_prompt()

    def process(self, prompt: str) -> intel.DandyPromptPythonFileIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.dandy_prompt_python_file_input_prompt(prompt),
            intel_class=intel.DandyPromptPythonFileIntel
        )


class TextToMarkdownPromptBot(Bot):
    llm_role = prompts.text_to_markdown_instruction_bot_prompt()

    def process(self, text: str) -> intel.TextToMarkdownIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.text_to_markdown_input_prompt(text),
            intel_class=intel.TextToMarkdownIntel
        )

from pathlib import Path

from dandy.llm import BaseLlmBot
from django.conf import settings

from django_spire.ai.prompt import prompts
from django_spire.ai.prompt import intel



class DandyPythonPromptBot(BaseLlmBot):
    instructions_prompt = prompts.dandy_prompt_python_file_instruction_bot_prompt()
    intel_class = intel.DandyPromptPythonFileIntel

    @classmethod
    def process(
            cls,
            prompt: str,

    ) -> intel.DandyPromptPythonFileIntel:
        """
            Takes in an enhanced prompt and turn it into a python file that uses the dandy library.
        """
        return cls.process_prompt_to_intel(
            prompt=prompts.dandy_prompt_python_file_input_prompt(prompt)
        )


class TextToMarkdownPromptBot(BaseLlmBot):
    instructions_prompt = prompts.text_to_markdown_instruction_bot_prompt()
    intel_class = intel.TextToMarkdownIntel

    @classmethod
    def process(
            cls,
            text: str,

    ) -> intel.TextToMarkdownIntel:
        """
            Takes in user text and converts it to properly formatted Markdown.
        """
        return cls.process_prompt_to_intel(
            prompt=prompts.text_to_markdown_input_prompt(text)
        )

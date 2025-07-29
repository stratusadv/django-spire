from pathlib import Path

from dandy.llm import BaseLlmBot
from django.conf import settings

from django_spire.ai.prompt import prompts
from django_spire.ai.prompt import intel

_PROMPT_OUTPUT_PATH = Path(settings.BASE_DIR, '.prompt_generator_output')
_MARKDOWN_OUTPUT_PATH = Path(settings.BASE_DIR, '.markdown')


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
        prompt_file = cls.process_prompt_to_intel(
            prompt=prompts.dandy_prompt_python_file_input_prompt(prompt)
        )

        Path(_PROMPT_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

        with open(Path(_PROMPT_OUTPUT_PATH, prompt_file.file_name), 'w') as f:
            f.write(prompt_file.source_code)

        print(f'Done ... saved to "{Path(_PROMPT_OUTPUT_PATH, prompt_file.file_name)}"')

        return prompt_file


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
        markdown_file = cls.process_prompt_to_intel(
            prompt=prompts.text_to_markdown_input_prompt(text)
        )

        Path(_MARKDOWN_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

        with open(Path(_MARKDOWN_OUTPUT_PATH, markdown_file.file_name), 'w') as f:
            f.write(markdown_file.markdown_content)

        print(f'Done ... saved to "{Path(_MARKDOWN_OUTPUT_PATH, markdown_file.file_name)}"')

        return markdown_file

from pathlib import Path

from dandy.llm import BaseLlmBot
from django.conf import settings

from django_spire.ai.prompt import prompts
from django_spire.ai.prompt import intel

_PROMPT_OUTPUT_PATH = Path(settings.BASE_DIR, '.prompt_generator_output')


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



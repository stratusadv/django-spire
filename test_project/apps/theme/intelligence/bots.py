from dandy.llm import BaseLlmBot

from test_project.apps.theme.intelligence import prompts
from test_project.apps.theme.intelligence import intel


class ThemeBot(BaseLlmBot):
    instructions_prompt = prompts.theme_instruction_prompt()
    intel_class = intel.ThemeIntel

    @classmethod
    def process(
            cls,
            user_input: str
    ) -> intel.ThemeIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.theme_user_input_prompt(user_input)
        )

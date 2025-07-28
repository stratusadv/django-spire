from dandy.llm import BaseLlmBot

from django_spire.ai.prompt.system import prompts
from django_spire.ai.prompt.system import intel


class SystemPromptBot(BaseLlmBot):
    instructions_prompt = prompts.system_prompt_instruction_bot_prompt()
    intel_class = intel.SystemPromptIntel


    @classmethod
    def process(
            cls,
            user_story: str

    ) -> intel.SystemPromptIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story)
        )

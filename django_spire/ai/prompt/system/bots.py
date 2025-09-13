from dandy.llm import BaseLlmBot, LlmConfigOptions

from django_spire.ai.prompt.system import prompts
from django_spire.ai.prompt.system import intel


"""
Role -> 
Task (Goal) -> 
Context ->
Guidelines ->
User Input ->
Expected Format ->
Constraints ->
"""


class SystemPromptRoleBot(BaseLlmBot):
    instructions_prompt = prompts.role_bot_prompt()
    intel_class = intel.SystemPromptResultIntel
    config_options = LlmConfigOptions(
        temperature=0.5
    )


    @classmethod
    def process(
            cls,
            user_story: str

    ) -> intel.SystemPromptResultIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story)
        )


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

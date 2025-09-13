from dandy.llm import BaseLlmBot, LlmConfigOptions

from django_spire.ai.prompt.system import prompts
from django_spire.ai.prompt.system import intel
from django_spire.ai.prompt.system.intel import SystemPromptIntel

"""
Role -> :) 
Task -> :)
Context -> Skipping for now!
Guidelines -> ;0
User Input -> Skipping for now!
Output Format -> ;0
Constraints -> Skipping for now!
"""

class RoleSystemPromptBot(BaseLlmBot):
    instructions_prompt = prompts.role_bot_prompt()
    intel_class = intel.SystemPromptResultIntel
    config_options = LlmConfigOptions(
        temperature=0.8
    )


    @classmethod
    def process(
            cls,
            user_story: str

    ) -> intel.SystemPromptResultIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story)
        )


class TaskSystemPromptBot(BaseLlmBot):
    instructions_prompt = prompts.task_bot_prompt()
    intel_class = intel.SystemPromptResultIntel
    config_options = LlmConfigOptions(
        temperature=0.2
    )


    @classmethod
    def process(
            cls,
            user_story: str

    ) -> intel.SystemPromptResultIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story)
        )


class GuidelinesSystemPromptBot(BaseLlmBot):
    instructions_prompt = prompts.guidelines_bot_prompt()
    intel_class = intel.SystemPromptResultIntel
    config_options = LlmConfigOptions(
        temperature=0.2
    )

    @classmethod
    def process(
            cls,
            user_story: str

    ) -> intel.SystemPromptResultIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story)
        )


class OutputFormatSystemPromptBot(BaseLlmBot):
    instructions_prompt = prompts.output_format_bot_prompt()
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

        role_future = RoleSystemPromptBot.process_to_future(user_story)
        task_future = TaskSystemPromptBot.process_to_future(user_story)
        guidelines_future = GuidelinesSystemPromptBot.process_to_future(user_story)
        output_format_future = OutputFormatSystemPromptBot.process_to_future(user_story)

        role = role_future.result
        task = task_future.result
        guidelines = guidelines_future.result
        output_format = output_format_future.result

        return SystemPromptIntel(
            role=role.result,
            task=task.result,
            guidelines=guidelines.result,
            output_format=output_format.result
        )

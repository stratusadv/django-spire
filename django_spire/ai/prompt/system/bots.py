from __future__ import annotations

from dandy import Bot, LlmConfigOptions, recorder_to_html_file

from django_spire.ai.prompt.system import prompts
from django_spire.ai.prompt.system import intel
from django_spire.ai.prompt.system.intel import SystemPromptIntel


class RoleSystemPromptBot(Bot):
    llm_role = prompts.role_bot_prompt()
    llm_config_options = LlmConfigOptions(temperature=0.5)

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class TaskSystemPromptBot(Bot):
    llm_role = prompts.task_bot_prompt()
    llm_config_options = LlmConfigOptions(temperature=0.5)

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class GuidelinesSystemPromptBot(Bot):
    llm_role = prompts.guidelines_bot_prompt()
    llm_config_options = LlmConfigOptions(temperature=0.2)

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class OutputFormatSystemPromptBot(Bot):
    llm_role = prompts.output_format_bot_prompt()
    llm_config_options = LlmConfigOptions(temperature=0.5)

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class SystemPromptBot(Bot):
    llm_role = prompts.system_prompt_instruction_bot_prompt()

    def process(self, user_story: str) -> intel.SystemPromptIntel:
        role_bot = RoleSystemPromptBot()
        task_bot = TaskSystemPromptBot()
        guidelines_bot = GuidelinesSystemPromptBot()
        output_format_bot = OutputFormatSystemPromptBot()

        # role_future = role_bot.process_to_future(user_story)
        # task_future = task_bot.process_to_future(user_story)
        # guidelines_future = guidelines_bot.process_to_future(user_story)
        # output_format_future = output_format_bot.process_to_future(user_story)

        role = role_bot.process(user_story)
        task = task_bot.process(user_story)
        guidelines = guidelines_bot.process(user_story)
        output_format = output_format_bot.process(user_story)

        return SystemPromptIntel(
            role=role.result,
            task=task.result,
            guidelines=guidelines.result,
            output_format=output_format.result
        )

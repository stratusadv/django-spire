from __future__ import annotations

from dandy import Bot

from django_spire.ai.prompt.system import intel, prompts


class RoleSystemPromptBot(Bot):
    role = prompts.role_bot_prompt()

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        self.llm.options.temperature = 0.5
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class TaskSystemPromptBot(Bot):
    role = prompts.task_bot_prompt()

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        self.llm.options.temperature = 0.5
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class GuidelinesSystemPromptBot(Bot):
    role = prompts.guidelines_bot_prompt()

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        self.llm.options.temperature = 0.2
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class OutputFormatSystemPromptBot(Bot):
    role = prompts.output_format_bot_prompt()

    def process(self, user_story: str) -> intel.SystemPromptResultIntel:
        self.llm.options.temperature = 0.5
        return self.llm.prompt_to_intel(
            prompt=prompts.system_user_input_prompt(user_story),
            intel_class=intel.SystemPromptResultIntel
        )


class SystemPromptBot(Bot):
    role = prompts.system_prompt_instruction_bot_prompt()

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

        return intel.SystemPromptIntel(
            role=role.result,
            task=task.result,
            guidelines=guidelines.result,
            output_format=output_format.result
        )

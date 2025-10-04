from __future__ import annotations

from django_spire.ai.prompt.system import bots
from django_spire.core.tests.test_cases import BaseTestCase


class PromptBotTestCase(BaseTestCase):
    def test_system_prompt_system_prompt(self):
        ISSUE_PROMPT = (
            "I am using jira to plan developer workloads And I want to be able to build very clear issues  that"
            "developers will be able to read understand and take action on to complete the goal."
            "I will give you details about a software development task that we have to achieve and I want you "
            "to return a short one sentence summary that the developer can read and understand the scope of the issue"
            "before they get into the details of it "
        )

        role_bot = bots.RoleSystemPromptBot()
        role_result = role_bot.process(ISSUE_PROMPT)
        self.assertIsNotNone(role_result)

        task_bot = bots.TaskSystemPromptBot()
        task_result = task_bot.process(ISSUE_PROMPT)
        self.assertIsNotNone(task_result)

        guidelines_bot = bots.GuidelinesSystemPromptBot()
        guidelines_result = guidelines_bot.process(ISSUE_PROMPT)
        self.assertIsNotNone(guidelines_result)

        output_format_bot = bots.OutputFormatSystemPromptBot()
        output_format_result = output_format_bot.process(ISSUE_PROMPT)
        self.assertIsNotNone(output_format_result)

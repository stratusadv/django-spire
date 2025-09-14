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

        role_bot = bots.RoleSystemPromptBot.process(ISSUE_PROMPT)
        self.assertIsNotNone(role_bot)

        task_bot = bots.TaskSystemPromptBot.process(ISSUE_PROMPT)
        self.assertIsNotNone(task_bot)


        guidelines_bot = bots.GuidelinesSystemPromptBot.process(ISSUE_PROMPT)
        self.assertIsNotNone(guidelines_bot)

        output_format_bot = bots.OutputFormatSystemPromptBot.process(ISSUE_PROMPT)
        self.assertIsNotNone(output_format_bot)
                
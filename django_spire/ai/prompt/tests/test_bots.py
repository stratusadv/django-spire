from django_spire.ai.prompt.system import bots
from django_spire.core.tests.test_cases import BaseTestCase

ROLE_PROMPT = (
            "I want to be able to feed something that I'm trying to accomplish and this LLM bot would describe the optimal role / persona and description needed for an LLM. "
        )

TASK_PROMPT = (
    "I want you to analyze the user's request and summarize it into a task or goal that another LLM would understand and give it clear direction on what it's supposed to accomplish "
)

ISSUE_PROMPT = (
            "I am using jira to plan developer workloads And I want to be able to build very clear issues  that"
            "developers will be able to read understand and take action on to complete the goal."
            "I will give you details about a software development task that we have to achieve and I want you "
            "to return a short one sentence summary that the developer can read and understand the scope of the issue"
            "before they get into the details of it "
)

class PromptBotTestCase(BaseTestCase):

    def test_role_system_prompt(self):
        print('------------ROLE PROMPT----------------')
        role_bot = bots.RoleSystemPromptBot.process(ROLE_PROMPT)
        print("ROLE")
        print(role_bot.result)
        print()

        task_bot = bots.TaskSystemPromptBot.process(ROLE_PROMPT)
        print('TASK')
        print(task_bot.result)
        print()

    def test_task_system_prompt(self):
        print('------------TASK PROMPT----------------')
        role_bot = bots.RoleSystemPromptBot.process(TASK_PROMPT)
        print("ROLE")
        print(role_bot.result)
        print()

        task_bot = bots.TaskSystemPromptBot.process(TASK_PROMPT)
        print('TASK')
        print(task_bot.result)
        print()

    def test_issue_system_prompt(self):
        print('------------ISSUE PROMPT----------------')
        role_bot = bots.RoleSystemPromptBot.process(ISSUE_PROMPT)
        print("ROLE")
        print(role_bot.result)
        print()

        task_bot = bots.TaskSystemPromptBot.process(ISSUE_PROMPT)
        print('TASK')
        print(task_bot.result)
        print()


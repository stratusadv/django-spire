from django_spire.ai.prompt.system import bots
from django_spire.core.tests.test_cases import BaseTestCase

GUIDELINES_PROMPT = (
    "your job is to create guidelines that help guide an LLM bot to achieve the users desired output.   "
)

OUTPUT_FORMAT_PROMPT = (
    "your job is to create the simplest format to return to the user that achieves the user's desired output."
)

ROLE_PROMPT = (
    "you are a technical writer that specializes in creating personas that are specific to achieving a task The user will input a task that they want to complete and your job is to create a persona for that person who is best suited to complete the task "
)

TASK_PROMPT = (
    "your job is to analyze the users input and summarize it into a clear task That the user is trying to accomplish."
)

ISSUE_PROMPT = (
    "I am using jira to plan developer workloads And I want to be able to build very clear issues  that"
    "developers will be able to read understand and take action on to complete the goal."
    "I will give you details about a software development task that we have to achieve and I want you "
    "to return a short one sentence summary that the developer can read and understand the scope of the issue"
    "before they get into the details of it "
)


class PromptBotTestCase(BaseTestCase):

    def test_guideline_system_prompt(self):
        print('------------GUIDELINES PROMPT----------------')
        role_bot = bots.RoleSystemPromptBot.process(GUIDELINES_PROMPT)
        print("ROLE")
        print(role_bot.result)
        print()

        task_bot = bots.TaskSystemPromptBot.process(GUIDELINES_PROMPT)
        print('TASK')
        print(task_bot.result)
        print()

        # guidelines_bot = bots.GuidelinesSystemPromptBot.process(GUIDELINES_PROMPT)
        # print('GUIDELINES')
        # print(guidelines_bot.result)
        # print()

        output_format_bot = bots.OutputFormatSystemPromptBot.process(GUIDELINES_PROMPT)
        print('OUTPUT FORMAT')
        print(output_format_bot.result)
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

        # guidelines_bot = bots.GuidelinesSystemPromptBot.process(ISSUE_PROMPT)
        # print('GUIDELINES')
        # print(guidelines_bot.result)
        # print()

        output_format_bot = bots.OutputFormatSystemPromptBot.process(ISSUE_PROMPT)
        print('OUTPUT FORMAT')
        print(output_format_bot.result)
        print()

    def test_output_format_system_prompt(self):
        print('------------OUTPUT FORMAT PROMPT----------------')
        role_bot = bots.RoleSystemPromptBot.process(OUTPUT_FORMAT_PROMPT)
        print("ROLE")
        print(role_bot.result)

        task_bot = bots.TaskSystemPromptBot.process(OUTPUT_FORMAT_PROMPT)
        print('TASK')
        print(task_bot.result)
        print()

        # guidelines_bot = bots.GuidelinesSystemPromptBot.process(OUTPUT_FORMAT_PROMPT)
        # print('GUIDELINES')
        # print(guidelines_bot.result)
        #
        output_format_bot = bots.OutputFormatSystemPromptBot.process(OUTPUT_FORMAT_PROMPT)
        print('OUTPUT FORMAT')
        print(output_format_bot.result)
        print()

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

        # guidelines_bot = bots.GuidelinesSystemPromptBot.process(ROLE_PROMPT)
        # print('GUIDELINES')
        # print(guidelines_bot.result)
        # print()

        output_format_bot = bots.OutputFormatSystemPromptBot.process(ROLE_PROMPT)
        print('OUTPUT FORMAT')
        print(output_format_bot.result)
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

        # guidelines_bot = bots.GuidelinesSystemPromptBot.process(TASK_PROMPT)
        # print('GUIDELINES')
        # print(guidelines_bot.result)
        # print()

        output_format_bot = bots.OutputFormatSystemPromptBot.process(TASK_PROMPT)
        print('OUTPUT FORMAT')
        print(output_format_bot.result)
        print()

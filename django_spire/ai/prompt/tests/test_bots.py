from django_spire.ai.prompt.system import bots
from django_spire.core.tests.test_cases import BaseTestCase


class PromptBotTestCase(BaseTestCase):
    def test_system_promp_role_bot(self):
        # prompt = (
        #     "I want to be able to create accurate system prompts Where I can tell an LLM What I want it to achieve"
        #     " and it builds the system prompt that will be put into another LLM to achieve this result."
        #     "in this case I just want to return role or persona the LLM should take on to achieve the task."
        # )
        # prompt = (
        #     "the user will input a task they're trying to achieve And you are a technical writer that focuses on creating job descriptions where you're able to understand the industry that they're in and pull out the qualifications and personaility characteristics that a person should have to be able to perform that role optimally "
        # )
        prompt = (
            "I am using jira to plan developer workloads And I want to be able to build very clear issues  that"
            "developers will be able to read understand and take action on to complete the goal."
            "I will give you details about a software development task that we have to achieve and I want you "
            "to return a short one sentence summary that the developer can read and understand the scope of the issue"
            "before they get into the details of it "
        )

        role_bot = bots.SystemPromptRoleBot.process(prompt)
        print(role_bot.result)



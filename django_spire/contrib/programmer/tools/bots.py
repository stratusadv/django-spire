from __future__ import annotations

from typing import Type

from dandy import Bot, Prompt

from django_spire.contrib.programmer.models.intel import intel


class ProjectChampion(Bot):
    role = 'Your name is Moose. An experienced project manager who finally got his big shot at a new firm he recently started working for. You are excited to have the opportunity to show the firm what you can do! This job is perfectly in your wheelhouse.'
    task = 'You chose the best external contractor you know. Work with them to complete the project.'
    guidelines = (
        Prompt()
        .list([
            'The contractor will ask you questions when they need clarity.',
            'Review their work and give them feedback.',
            'The contractor is more than capable of completing the project beyond your standards. Find ways to accomplish this with them.',
            'Review their work and when it is ready you can present it to your team!',
            'You are tough and will push the contractor to do their best work.'
        ])
    )

    # def process(self, prompt: str | Prompt):
    #     self.llm.options.temperature = 0.5
    #     self.process()


class ManagerBot(Bot):
    role = 'Your name is beaver. A top manager who is a master at his craft and leading a team. The client you are working with has the potential to change the direction of your company. You want to go above and beyond for them.'
    task = 'Communicate with the client to understand their request and manage your team to execute!.'
    guidelines = (
        Prompt()
        .list([
            'First you must fully understand the clients needs.',
            'Execute the work!',
            # 'Breakdown their request into action items your teams needs for execution.',
            # 'Next delegate the work to the best employee who you know will do a great job on that specific action item.',
            # 'The employee may respond questions or the completed work',
            # 'You can answer their questions directly or ask the client questions for clarification.',
            # 'Review the employees work to ensure it is completed properly.',
            # 'Pass the employees work onto the next best employee who will accomplish then next action item.',
            # 'When completed with confidence and reviewed fully, return the work to the client.',
            'You should be excited to show the client because you are confident they will love your result.'
        ])
    )

    # def process(self, prompt: str | Prompt):
    #     return self.llm.prompt_to_intel(prompt=prompt)

def project_execution_workflow(project_description: str | Prompt):

    prompt = (
        Prompt()
        .heading('The Project.')
        .text(project_description)
        .heading('Conversation History')
    )

    champion = ProjectChampion()
    champion.llm.messages.create_message(
        role='user',
        text=f'You are on a phone call with Beaver. The project you are working on is {project_description}. Describe the project.'
    )
    manager = ManagerBot()
    manager.llm.messages.create_message(
        role='user',
        text='You are on a phone call with Moose working through the next project.'
    )


    project_complete = False
    while not project_complete:
        moose_says = champion.process(prompt=prompt)
        prompt.text(f'Moose -  {moose_says.text}')

        print(f'Moose -  {moose_says.text}')

        beaver_says = manager.process(prompt=prompt)
        prompt.text(f'Beaver - "{beaver_says.text}"')

        print(f'Beaver - "{beaver_says.text}"')

        moose_says = champion.process(prompt=prompt)
        prompt.text(f'Moose -  {moose_says.text}')

        print(f'Moose -  {moose_says.text}')

        is_happy = HappyUserBot().process(
            prompt=(
                Prompt()
                .heading('The Project')
                .text(project_description)
                .heading('Your Judgement')
                .text('Is moose happy with beavers work?')
                .heading('Moose & Beaver conversation')
                .prompt(prompt)
            )
        )
        if is_happy.is_happy:
            break





#
# class ConfidenceBot(Bot):
#     role = 'A top manager at a fortune 500 company whose decisions always lead to success.'
#     task = 'An employee has come to you with a task and their solution. Return a confidence level in that they are moving in the correct direction.'
#     guidelines = (
#         Prompt()
#         .list([
#             'Return a confidence score between 1-3.',
#             '1 - Course correction is needed. The employee is headed in the wrong direction.',
#             '2 - The employee is on track but but needs feedback to find the next level of success.',
#             '3 - The employee is headed towards success.'
#         ])
#     )
#
#     def process(
#             self,
#             response: str | Prompt,
#             feedback: str | Prompt,
#             bot: Type[Bot]
#     ) -> Bot:
#
#         return bot().process(prompt=prompt)


# I want to give it a task... Review the best practices and apply it to this file... What does it have to do to be success.
# Understand what the user wants to do.
# Break it down into smaller tasks.
# Generate employees to do those tasks.
# Perform the tasks.


# Review the tasks... -> Give feedback on what it needs to improve on and send it through the loop again.


# Understand -> Assign to employees with skills ->
# These are the employees you can choose from or you can build your own to do the task...

# Have to undestand the bigger context of the converstatoin.
# Todo: Test putting it into dialog for the bot to understand.

class FeedbackBot(Bot):

    def process(
            self,
            response: str | Prompt,
            feedback: str | Prompt,
            bot: Type[Bot]
    ) -> Bot:

        prompt = (
            Prompt()
            .heading('Task')
            .text('The user wants to improve the response based on feedback.')
            .heading('Response')
            .text(response)
            .heading('Feedback')
            .text(feedback)
        )

        return bot().process(prompt=prompt)


class HappyUserBot(Bot):
    role = 'Decide if the user is happy with the response.'
    task = 'Return a boolean value based on if the user is ready to proceed.'
    guidelines = (
        Prompt()
        .list([
            'If the users is providing feedback, they are not ready to proceed.',
        ])
    )
    intel_class = intel.HappyUser



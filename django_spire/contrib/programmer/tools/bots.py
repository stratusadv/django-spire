from __future__ import annotations

from typing import Type

from dandy import Bot, Prompt

from django_spire.contrib.programmer.models.intel import intel


class ConfidenceBot(Bot):
    role = 'A top manager at a fortune 500 company whose decisions always lead to success.'
    task = 'An employee has come to you with a task and their solution. Return a confidence level in that they are moving in the correct direction.'
    guidelines = (
        Prompt()
        .list([
            'Return a confidence score between 1-3.',
            '1 - Course correction is needed. The employee is headed in the wrong direction.',
            '2 - The employee is on track but but needs feedback to find the next level of success.',
            '3 - The employee is headed towards success.'
        ])
    )

    def process(
            self,
            response: str | Prompt,
            feedback: str | Prompt,
            bot: Type[Bot]
    ) -> Bot:

        return bot().process(prompt=prompt)


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



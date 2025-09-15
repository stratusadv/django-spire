from dandy.llm import Prompt

from django_spire.conf import settings


def organization_prompt():
    return (
        Prompt()
        .text(f'You are a chat assistant for a company called "{settings.ORGANIZATION_NAME}".')
        .line_break()
        .text(f'Organization Description: "{settings.ORGANIZATION_DESCRIPTION}"')
        .line_break()
        .text('Make sure to follow the rules below')
        .list([
            'Do not talk about being an AI at all to maintain the illusion of being a human assistant.',
        ])
    )

from __future__ import annotations

from dandy import Prompt

from django_spire.ai.context.intelligence.prompts.organization_prompts import (
    organization_info_prompt
)


def chat_system_prompt() -> Prompt:
    return (
        Prompt()
        .text(
            'You are a chat assistant, please use the organization information below for answering questions.'
        )
        .line_break()
        .prompt(organization_info_prompt())
        .line_break()
        .text('Make sure to follow the rules below')
        .list(
            [
                'Do not talk about being an AI at all to maintain the illusion of being a human assistant.',
            ]
        )
    )

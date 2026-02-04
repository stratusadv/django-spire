from __future__ import annotations

from dandy import Prompt


def presentation_instruction_prompt() -> Prompt:
    return (
        Prompt()
        .title('Presentation Operations')
        .line_break()
        .heading('Purpose')
        .text('This prompt provides instructions for Presentation operations.')
        .line_break()
        .heading('Instructions')
        .ordered_list([
            'Instruction 1',
            'Instruction 2',
            'Instruction 3',
        ])
        .line_break()
    )


def presentation_user_input_prompt(user_input: str) -> Prompt:
    return (
        Prompt()
        .heading('Presentation Request')
        .text('The user wants to perform the following operation:')
        .text('')
        .text(user_input)
        .text('')
    )

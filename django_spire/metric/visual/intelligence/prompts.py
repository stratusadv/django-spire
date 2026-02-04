from __future__ import annotations

from dandy import Prompt


def visual_instruction_prompt() -> Prompt:
    return (
        Prompt()
        .title('Visual Operations')
        .line_break()
        .heading('Purpose')
        .text('This prompt provides instructions for Visual operations.')
        .line_break()
        .heading('Instructions')
        .ordered_list([
            'Instruction 1',
            'Instruction 2',
            'Instruction 3',
        ])
        .line_break()
    )


def visual_user_input_prompt(user_input: str) -> Prompt:
    return (
        Prompt()
        .heading('Visual Request')
        .text('The user wants to perform the following operation:')
        .text('')
        .text(user_input)
        .text('')
    )

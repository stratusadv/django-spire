from __future__ import annotations

from dandy import Prompt


def infinite_scrolling_instruction_prompt() -> Prompt:
    return (
        Prompt()
        .title('Infinite Scrolling Operations')
        .line_break()
        .heading('Purpose')
        .text('This prompt provides instructions for Infinite Scrolling operations.')
        .line_break()
        .heading('Instructions')
        .ordered_list([
            'Instruction 1',
            'Instruction 2',
            'Instruction 3',
        ])
        .line_break()
    )


def infinite_scrolling_user_input_prompt(user_input: str) -> Prompt:
    return (
        Prompt()
        .heading('Infinite Scrolling Request')
        .text('The user wants to perform the following operation:')
        .text('')
        .text(user_input)
        .text('')
    )

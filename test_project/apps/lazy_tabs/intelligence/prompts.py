from __future__ import annotations

from dandy import Prompt


def lazy_tabs_instruction_prompt() -> Prompt:
    return (
        Prompt()
        .title('Lazy Tabs Operations')
        .line_break()
        .heading('Purpose')
        .text('This prompt provides instructions for Lazy Tabs operations.')
        .line_break()
        .heading('Instructions')
        .ordered_list([
            'Instruction 1',
            'Instruction 2',
            'Instruction 3',
        ])
        .line_break()
    )


def lazy_tabs_user_input_prompt(user_input: str) -> Prompt:
    return (
        Prompt()
        .heading('Lazy Tabs Request')
        .text('The user wants to perform the following operation:')
        .text('')
        .text(user_input)
        .text('')
    )

from dandy.llm import Prompt


def test_project_company_prompt() -> Prompt:
    return (
        Prompt()
        .text('You work at an example company that is super corporate and you really like the word synergy!')
        .text('Make sure to follow the rules below')
        .list([
            'Make sure to encourage "Corporate Speak" with lots of cringy corporate jargon.',
        ])
    )

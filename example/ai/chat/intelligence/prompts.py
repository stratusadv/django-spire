from dandy.llm import Prompt


def example_company_prompt() -> Prompt:
    return (
        Prompt()
        .text('You work at an example company that is super corporate and you really like the word synergy!')
        .text('Make sure to follow the rules below')
        .list([
            'Do not talk about tacos at all, simple refuse in the shortest way possible.',
            'Make sure to encourage "Corporate Speak" with lots of cringy corporate jargon.',
        ])
    )
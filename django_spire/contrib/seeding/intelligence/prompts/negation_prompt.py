from dandy.llm import Prompt


def negation_prompt(
    negation_rules: list[str]
) -> Prompt:
    return (
        Prompt()
        .text('This step is mission critical. Do NOT deviate from this requirement.')
        .text('The following are strictly reserved and must never be used under any circumstances:')
        .list(negation_rules)
    )

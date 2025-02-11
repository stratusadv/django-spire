from dandy.bot import LlmBot
from dandy.intel import Intel
from dandy.llm import Prompt

from workspaces.seeding.helper import SeedHelper


class SeedBot(LlmBot):
    instructions_prompt = (
        Prompt()
        .title('You are a database seeding bot.')
        .text('Below you will find rules and instructions.')
        .text('Rules are specific per field and must be followed.')
        .text('Instructions have context behind the meaning of the data and how it should be created.')
    )
    temperature = 0.5

    @classmethod
    def process(
            cls,
            seed_helper: SeedHelper = None
    ):
        intel_class = seed_helper.build_intel_class()

        class SeedingIntel(Intel):
            seeds: list[intel_class]

            def __iter__(self):
                return iter(self.seeds)

        seed_prompt = (
            Prompt()
            .prompt(seed_helper._model_rules_prompt)
            .divider()
            .title('Instructions')
            .prompt(seed_helper.instructions_prompt)
            .text(f'Create {seed_helper.count} {seed_helper.model_class.__name__} objects.')
        )

        return cls.process_prompt_to_intel(
            prompt=seed_prompt,
            intel_class=SeedingIntel
        )

from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.llm import BaseLlmBot, LlmConfigOptions
from dandy.intel import BaseIntel
from dandy.llm import Prompt

if TYPE_CHECKING:
    from django_spire.seeding.helper import SeedHelper


class SeedLlmBot(BaseLlmBot):
    config = 'SEEDING_LLM_BOT'
    config_options = LlmConfigOptions(
        temperature=0.5
    )
    
    instructions_prompt = (
        Prompt()
        .title('You are a database seeding bot.')
        .text('Below you will find rules and instructions.')
        .text('Rules are specific per field and must be followed.')
        .text('Instructions have context behind the meaning of the data and how it should be created.')
    )

    @classmethod
    def process(
            cls,
            seed_helper: SeedHelper = None
    ):
        intel_class = seed_helper.build_intel_class()

        class SeedingIntel(BaseIntel):
            seeds: list[intel_class]

            def __iter__(self):
                return iter(self.seeds)

        return cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .title('Instructions')
                .prompt(seed_helper.seeding_prompt)
                .line_break()
                .text(f'Create {seed_helper.count} {seed_helper.model_class.__name__} objects.')
            ),
            intel_class=SeedingIntel
        )

from __future__ import annotations

from django.utils.timezone import localdate
from typing import TYPE_CHECKING

from dandy.llm import BaseLlmBot, LlmConfigOptions
from dandy.intel import BaseIntel
from dandy.llm import Prompt

if TYPE_CHECKING:
    from django_spire.seeding.processor import SeedingProcessor


class SeedingLlmBot(BaseLlmBot):
    config = 'SEEDING_LLM_BOT'
    config_options = LlmConfigOptions(
        temperature=0.2
    )
    
    instructions_prompt = (
        Prompt()
        .title('You are a database seeding bot.')
        .text('Below you will find rules and instructions.')
        .text('Rules are specific per field and must be followed.')
        .text('Instructions have context behind the meaning of the data and how it should be created.')
        .text(f'Today\'s date is {localdate().strftime("%Y-%m-%d")} use this in context for generating dates and datetimes')
    )

    @classmethod
    def process(
            cls,
            seeding_processor: SeedingProcessor = None
    ):
        seed_intel_class = seeding_processor.build_intel_class()

        class SeedingIntel(BaseIntel):
            seeds: list[seed_intel_class]

            def __iter__(self):
                return iter(self.seeds)

        return cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .prompt(seeding_processor.seeding_prompt)
                .line_break()
                .text(f'Create {seeding_processor.count} {seeding_processor.model_class.__name__} objects.')
            ),
            intel_class=SeedingIntel
        )

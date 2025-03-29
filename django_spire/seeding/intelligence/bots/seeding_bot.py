from __future__ import annotations

from django.utils.timezone import localdate
from typing import TYPE_CHECKING

from dandy.llm import BaseLlmBot, LlmConfigOptions, Prompt
from dandy.intel import BaseIntel

from django_spire.core.converters import django_to_pydantic_model

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
        seed_intel_class_2 = seeding_processor.build_intel_class()
        seed_intel_class = django_to_pydantic_model(
            model_class=seeding_processor.model_class,
            base_class=BaseIntel,
            include_fields=seeding_processor.include_fields,
            exclude_fields=seeding_processor.exclude_fields
        )

        # print('CORRECT JSON SCHEMA')
        print(seed_intel_class.model_json_schema())

        print('---')
        print()
        # print()
        # print('WRONG JSON SCHEMA')
        print(seed_intel_class_2.model_json_schema())



        class SeedingIntel(BaseIntel):
            items: list[seed_intel_class]

            def __iter__(self):
                return iter(self.items)

        return cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .prompt(seeding_processor.seeding_prompt)
                .line_break()
                .text(f'Create {seeding_processor.count} {seeding_processor.model_class.__name__} objects.')
            ),
            intel_class=SeedingIntel
        )

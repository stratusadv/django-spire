from __future__ import annotations

from django.utils.timezone import localdate

from dandy.llm import LlmBot, BaseLlmBot, LlmConfigOptions, Prompt
from dandy.core.cache import cache_to_sqlite

from django_spire.seeding.intelligence.intel import AttrsIntel, SeedingIntel


class SeedingAttrsLlmBot(BaseLlmBot):
    config = 'SEEDING_ATTR_LLM_BOT'

    @classmethod
    @cache_to_sqlite('seeding')
    def process(cls, attr_type: type, description: str, count: int) -> Any:
        attrs_intel = cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .text(f'Create {count} {description}')
            ),
            intel_class=AttrsIntel
        )

        return [ attr_type(attr) for attr in attrs_intel.items ]


class LlmSeedingBot(LlmBot):
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
    # @cache_to_sqlite('seeding')
    def process(cls, *args, **kwargs) -> list[dict]:
        intel_data = super().process(*args, **kwargs)
        return intel_data.model_dump(mode='json')['items']


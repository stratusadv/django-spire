from __future__ import annotations

from django.utils.timezone import localdate

from dandy import Bot, Prompt


class LlmFieldSeedingBot(Bot):
    llm_config = 'SEEDING_LLM_BOT'

    role = 'An expert at generating data and following specifications.'
    task = 'Create seed data for a software application.'
    guidelines = (
        Prompt()
        .text('ALL FIELDS ARE REQUIRED TO HAVE DATA.')
        .text('Instructions have context behind the meaning of the data and how it should be created.')
        .text(f'Today\'s date is {localdate().strftime("%Y-%m-%d")} use this in context for generating dates and datetimes')
    )

    def process(self, prompt: Prompt, intel_class) -> list[dict]:
        self.llm.options.temperature = 0.5

        intel_data = self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class
        )
        return intel_data.model_dump(mode='json')['items']

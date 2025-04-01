from django_spire.seeding.intelligence.bots import LlmSeedingBot
from django_spire.seeding.seeder import BaseSeeder

from dandy.llm import Prompt
from dandy.intel import BaseIntel


class LlmSeeder(BaseSeeder):
    keyword = 'llm'
    prompt = None

    @classmethod
    def seed(cls, count = 1) -> list[dict]:
        # Todo: Need to turn fields into llm call?
        # How does that work with pydantic?

        class SeedingIntel(BaseIntel):
            pass
        #     items: list[seed_intel_class]
        #
        #     def __iter__(self):
        #         return iter(self.items)

        prompt = (
            Prompt()
            .prompt(cls.prompt)
            .heading('Seed Count')
            # .text(f'Create {count} {self.model_class.__name__}')
        )

        intel_data = LlmSeedingBot.process(
            prompt=prompt,
            intel_class=SeedingIntel
        )

        return intel_data

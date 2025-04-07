# from django_spire.seeding.intelligence.bots import LlmSeedingBot
# from django_spire.seeding.seeder import BaseSeeder
#
# from dandy.llm import Prompt
# from dandy.intel import BaseIntel
#
#
# class LlmSeeder(BaseSeeder):
#     keyword = 'llm'
#
#     def __init__(
#             self,
#             fields: dict = None,
#             default_to: str = "llm",
#             prompt: Prompt = None,
#      ):
#         super().__init__(fields, default_to)
#         self.prompt = prompt or Prompt()
#
#
#     def seed(self, manager, count = 1) -> list[dict]:
#         # Todo: Need to turn fields into llm call?
#         # How does that work with pydantic?
#
#         class SeedingIntel(BaseIntel):
#             pass
#         #     items: list[seed_intel_class]
#         #
#         #     def __iter__(self):
#         #         return iter(self.items)
#
#         prompt = (
#             Prompt()
#             .prompt(self.prompt)
#             .heading('Seed Count')
#             # .text(f'Create {count} {self.model_class.__name__}')
#         )
#
#         intel_data = LlmSeedingBot.process(
#             prompt=prompt,
#             intel_class=SeedingIntel
#         )
#
#         return intel_data

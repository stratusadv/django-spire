from django_spire.contrib.seeder.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeder.field.seed.llm_seed import LlmFieldSeed


class LlmFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def automatic(field_type: type) -> LlmFieldSeed:
        return LlmFieldSeed(field_type=field_type)

    @staticmethod
    def prompt(field_type: type, prompt: str) -> LlmFieldSeed:
        return LlmFieldSeed(field_type=field_type, prompt=prompt)

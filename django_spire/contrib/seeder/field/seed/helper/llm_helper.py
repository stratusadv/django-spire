from django_spire.contrib.seeder.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeder.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeder.field.seed.llm_seed import LlmFieldSeed


class LlmFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def automatic(field_type: type) -> BaseFieldSeed:
        return LlmFieldSeed(field_type=field_type)

    @staticmethod
    def prompt(field_type: type, prompt: str) -> BaseFieldSeed:
        return LlmFieldSeed(field_type=field_type, prompt=prompt)

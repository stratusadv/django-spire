from __future__ import annotations

from typing import Any

from dandy import BaseIntel, Bot, Prompt
from django.utils.timezone import localdate
from pydantic import create_model

from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.exclude_seed import ExcludeMutateFieldSeed
from django_spire.contrib.seeding.seed.seed import Seed
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed


class FieldSeedingBot(Bot):
    role = 'Data Generation Expert'
    task = 'Create field seed data for a software application based on request.'
    guidelines = Prompt().unordered_random_list(
        [
            'Field names have context behind the meaning of the data and how it should be created.',
            f'The date for today is {localdate().strftime("%Y-%m-%d")} use this for context.',
            'The user will provide you with seeder name, filled fields and missing fields.',
            'Use the already filled fields as context on how to fill the empty ones.',
        ]
    )

    def process(self, seeder_name: str, fields_seeds: dict[str, Any], seed_index: int) -> Seed:
        fields_dict = {}

        prompt = Prompt()

        prompt.heading(seeder_name)

        prompt.sub_heading('Already Filled Fields for Context')

        non_llm_fields_values = self._process_non_llm_fields(
            fields_seeds=fields_seeds, seed_index=seed_index
        )

        for field, value in non_llm_fields_values.items():
            prompt.text(f'{field}: {value}')

        prompt.line_break()

        prompt.sub_heading('Empty Fields Required to have Data')

        fields_llm_seeds = {
            field: seed for field, seed in fields_seeds.items() if isinstance(seed, LlmFieldSeed)
        }

        for field, llm_seed in fields_llm_seeds.items():
            fields_dict[field] = (llm_seed.field_type, ...)
            if llm_seed.prompt:
                prompt.text(f'{field}: "{llm_seed.prompt}"')
            else:
                prompt.text(f'{field}: "No description provided, use context"')

        if fields_dict:
            FieldIntel = create_model('FieldIntel', __base__=BaseIntel, **fields_dict)

            field_intel = self.llm.prompt_to_intel(prompt=prompt, intel_class=FieldIntel)

            return Seed({**field_intel.model_dump(), **non_llm_fields_values})

        return Seed(non_llm_fields_values)

    @staticmethod
    def _process_non_llm_fields(fields_seeds: dict[str, Any], seed_index: int) -> dict[str, Any]:
        fields_values = {}

        for field, seed in fields_seeds.items():
            if isinstance(seed, ExcludeMutateFieldSeed):
                possible_seed = seed.generate_value(seed_index)

                if possible_seed:
                    fields_values[field] = possible_seed.generate_value(seed_index)

            elif not isinstance(seed, ExcludeFieldSeed) and not isinstance(seed, LlmFieldSeed):
                fields_values[field] = seed.generate_value(seed_index=seed_index)

        return fields_values

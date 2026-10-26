from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dandy import BaseIntel, Bot, Prompt
from django.utils.timezone import localdate
from pydantic import create_model

from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.exclude_seed import ExcludeMutateFieldSeed
from django_spire.contrib.seeding.seed.seed import Seed
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed

if TYPE_CHECKING:
    from django.db import models


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

    def process(
        self,
        seeder_name: str,
        fields_seeds: dict[str, Any],
        seed_index: int,
        model_class: type[models.Model] | None = None,
    ) -> Seed:
        pre_llm_fields, llm_fields, post_llm_fields = self._split_fields_around_llm(fields_seeds)

        row_values = self._process_non_llm_fields(
            fields_seeds=pre_llm_fields, seed_index=seed_index, model_class=model_class
        )

        if llm_fields:
            llm_values = self._generate_llm_fields(
                seeder_name=seeder_name, llm_fields=llm_fields, filled_fields=row_values
            )

            row_values.update(llm_values)

            row_values.update(
                self._process_non_llm_fields(
                    fields_seeds=post_llm_fields,
                    seed_index=seed_index,
                    model_class=model_class,
                    row_values=row_values,
                )
            )

        return Seed(row_values)

    @staticmethod
    def _split_fields_around_llm(
        fields_seeds: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        pre_llm_fields: dict[str, Any] = {}
        llm_fields: dict[str, Any] = {}
        post_llm_fields: dict[str, Any] = {}
        seen_llm = False

        for field, seed in fields_seeds.items():
            if isinstance(seed, LlmFieldSeed):
                llm_fields[field] = seed
                seen_llm = True
            elif seen_llm:
                post_llm_fields[field] = seed
            else:
                pre_llm_fields[field] = seed

        return pre_llm_fields, llm_fields, post_llm_fields

    def _generate_llm_fields(
        self, seeder_name: str, llm_fields: dict[str, LlmFieldSeed], filled_fields: dict[str, Any]
    ) -> dict[str, Any]:
        prompt = Prompt()

        prompt.heading(seeder_name)

        prompt.sub_heading('Already Filled Fields for Context')

        for field, value in filled_fields.items():
            prompt.text(f'{field}: {value}')

        prompt.line_break()

        prompt.sub_heading('Empty Fields Required to have Data')

        fields_dict = {}

        for field, llm_seed in llm_fields.items():
            fields_dict[field] = (llm_seed.field_type, ...)
            if llm_seed.prompt:
                prompt.text(f'{field}: "{llm_seed.prompt}"')
            else:
                prompt.text(f'{field}: "No description provided, use context"')

        field_intel_class = create_model('FieldIntel', __base__=BaseIntel, **fields_dict)

        field_intel = self.llm.prompt_to_intel(prompt=prompt, intel_class=field_intel_class)

        return field_intel.model_dump()

    @staticmethod
    def _process_non_llm_fields(
        fields_seeds: dict[str, Any],
        seed_index: int,
        model_class: type[models.Model] | None = None,
        row_values: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        fields_values = dict(row_values or {})

        for field, seed in fields_seeds.items():
            if isinstance(seed, ExcludeMutateFieldSeed):
                possible_seed = seed.generate_value(seed_index)

                if possible_seed:
                    fields_values[field] = possible_seed.generate_value(seed_index)

            elif not isinstance(seed, ExcludeFieldSeed) and not isinstance(seed, LlmFieldSeed):
                fields_values[field] = seed.generate_value_context(
                    seed_index, model_class=model_class, field_name=field, row_values=fields_values
                )

        return fields_values

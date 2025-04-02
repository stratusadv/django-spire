from __future__ import annotations

from dandy.llm import Prompt
from dandy.intel import BaseIntel

from django_spire.core.converters import django_to_pydantic_model, fake_model_field_value
from django_spire.seeding.field.base import BaseFieldSeeder
from django_spire.seeding.field.enums import FieldSeederTypesEnum
from django_spire.seeding.intelligence.bots.field_seeding_bots import LlmFieldSeedingBot


class DjangoFieldLlmSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.LLM

    def seed(self, model_seeder, count: int = 1,) -> list[dict]:

        include_fields = list(self.seeder_fields.keys())

        seed_intel_class = django_to_pydantic_model(
            model_class=model_seeder.model_class,
            base_class=BaseIntel,
            include_fields=include_fields
        )

        class SeedingIntel(BaseIntel):
            items: list[seed_intel_class]

            def __iter__(self):
                return iter(self.items)

        prompt = (
            Prompt()
            .prompt(self.field_prompt)
            .heading('Seed Count')
            .text(f'Create {count} {model_seeder.model_class.__name__}')
        )

        intel_data = LlmFieldSeedingBot.process(
            prompt=prompt,
            intel_class=SeedingIntel
        )

        return intel_data

    @property
    def field_prompt(self) -> Prompt:
        if any(len(info) > 1 for info in self.seeder_fields.values()):
            field_prompt = (
                Prompt()
                .heading('Fields Context Data')
                .list([
                    f'{name}: {info[1]}'
                    for name, info in self.seeder_fields.items()
                    if info[0] == 'llm' and len(info) > 1
                ])
            )
        else:
            field_prompt = Prompt()

        return field_prompt



class DjangoFieldFakerSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.FAKER

    def seed(self, model_seeder, count = 1) -> list[dict]:
        data = []
        for i in range(count):
            row = {}
            for field_name, faker_config in self.seeder_fields.items():
                faker_method = faker_config[1:] if len(faker_config) > 1 else None
                row[field_name] = fake_model_field_value(
                    model_class=model_seeder.model_class,
                    field_name=field_name,
                    faker_method=faker_method
                )
            data.append(row)
        return data

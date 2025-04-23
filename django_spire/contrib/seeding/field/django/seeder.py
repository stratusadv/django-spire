from __future__ import annotations

from dandy.llm import Prompt
from dandy.intel import BaseIntel

from django_spire.core.converters import django_to_pydantic_model, fake_model_field_value
from django_spire.contrib.seeding.field.base import BaseFieldSeeder
from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum
from django_spire.contrib.seeding.intelligence.bots.field_seeding_bots import LlmFieldSeedingBot


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

        # Base parts of the prompt that are common between batches
        base_prompt = (
            Prompt()
            .heading('General Seeding Rules')
            .list(['Create data for each field provided.'])
            .heading('Field Rules & Context')
            .prompt(self.field_prompt)
        )

        if count <= 25:
            # Create a prompt for the full count since it's within a single batch
            prompt = (
                Prompt()
                .heading('Seed Count')
                .text(f'Create {count} {model_seeder.model_class.__name__}')
                .prompt(base_prompt)
            )

            intel_data = LlmFieldSeedingBot.process(
                prompt=prompt,
                intel_class=SeedingIntel
            )
        else:
            # Process in batches of 25 using futures. Seems like that is the limit for good results
            futures = []
            completed_futures = []
            max_futures = 4
            intel_data = []

            total_batches = (count + 24) // 25

            for batch_index in range(total_batches):
                batch_count = 25 if (batch_index < total_batches - 1) else count - 25 * batch_index

                batch_prompt = (
                    Prompt()
                    .heading('Seed Count')
                    .text(f'Create {batch_count} {model_seeder.model_class.__name__}')
                    .prompt(base_prompt)
                )

                future = LlmFieldSeedingBot.process_to_future(
                    prompt=batch_prompt,
                    intel_class=SeedingIntel
                )
                futures.append(future)

                # Only send max_futures calls at a time or when it's the last batch.
                if len(futures) >= max_futures or batch_index == total_batches - 1:
                    print(f'-----> Seeding batch {batch_index + 1} of {total_batches}')
                    for future in futures:
                        intel_data.extend(future.result)
                        completed_futures.append(future)

                    futures = []

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
                try:
                    row[field_name] = fake_model_field_value(
                        model_class=model_seeder.model_class,
                        field_name=field_name,
                        faker_method=faker_method
                    )
                except Exception as e:
                    raise ValueError(f"Error generating faker value for field '{field_name}': {e}")
            data.append(row)
        return data

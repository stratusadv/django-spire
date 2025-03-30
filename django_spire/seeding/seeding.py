from __future__ import annotations

from abc import ABC, abstractmethod

from django.db.models.base import Model
from typing import Type

from dandy.llm import Prompt
from dandy.intel import BaseIntel

from django_spire.core.converters import django_to_pydantic_model, fake_model_field_value
from django_spire.seeding.intelligence.bots import LlmSeedingBot


class ModelSeeding:

    def __init__(
            self,
            model_class: Type[Model],
            fields: dict[str, tuple],
            prompt: Prompt = None,
            include_fields: list[str] = None,
            exclude_fields: list[str] = None

    ):
        model_class_fields_names = [field.name for field in model_class._meta.fields]

        # All defined fields must be a valid model field.
        if any(field not in model_class_fields_names for field in fields.keys()):
            raise ValueError(f'Invalid field name(s): {", ".join(fields.keys() - model_class_fields_names)}')

        self.model_class = model_class
        self.prompt = prompt or Prompt()

        self.fields = fields

        self.exclude_fields = exclude_fields or []
        self.include_fields = include_fields or []

    def filter_fields(self, seed_type: str) -> dict:
        llm_fields = {}
        for key, value in self.fields.items():
            if not isinstance(value, tuple):
                value = (value,)
            if value and value[0] == seed_type:
                llm_fields[key] = self.fields[key]
        return llm_fields

    def _callable_seed_data(self, count=1) -> list[dict]:
        return ModelCallableSeeds(
            model_class=self.model_class,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields,
            count=count
        ).generate_data()

    def _faker_seed_data(self, count=1) -> list[dict]:
        return ModelFakerSeeds(
            model_class=self.model_class,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields,
            count=count
        ).generate_data()

    def _llm_seed_data(self, count=1) -> list[dict]:
        llm_fields = self.filter_fields('llm')

        # Add extra field info to prompt
        if any(len(info) > 1 for info in llm_fields.values()):
            field_prompt = (
                Prompt()
                .heading('Fields Context Data')
                .list([
                    f'{name}: {info[1]}'
                    for name, info in llm_fields.items()
                    if len(info) > 1
                ])
            )

            self.prompt = self.prompt.prompt(field_prompt)

        return ModelLlmSeeds(
            model_class=self.model_class,
            include_fields=list(llm_fields.keys()),
            count=count
        ).generate_data(prompt=self.prompt)

    def _static_seed_data(self, count=1) -> list[dict]:
        return ModelStaticSeeds(
            model_class=self.model_class,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields,
            count=count
        ).generate_data()

    def seed_data(self, count=1) -> list[dict]:
        llm_seed_data = self._llm_seed_data(count)
        faker_seed_data = self._faker_seed_data(count)
        static_seed_data = self._static_seed_data(count)
        callable_seed_data = self._callable_seed_data(count)

        return [
            {**d1, **d2, **d3, **d4}
            for d1, d2, d3, d4 in zip(llm_seed_data, faker_seed_data, static_seed_data, callable_seed_data)
        ]

    def generate_model_objects(
            self,
            count: int = 1,
            fields: dict | None = None,
            clear_cache: bool = False
    ):
        # Todo: Overwrite field data.
        return [self.model_class(**seed_data) for seed_data in self.seed_data(count)]

    def seed_database(
            self,
            count: int = 1,
            fields: dict | None = None,
            clear_cache: bool = False
    ):
        model_objects = self.generate_model_objects(count, fields, clear_cache)
        return self.model_class.objects.bulk_create(model_objects)


class ModelBaseSeeds(ABC):

    def __init__(
            self,
            model_class: Type[Model],
            include_fields: list[str] = None,
            exclude_fields: list[str] = None,
            count: int = 1
    ):
        self.model_class = model_class
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields
        self.count = count

    @abstractmethod
    def generate_data(self, *args, **kwargs):
        pass


class ModelLlmSeeds(ModelBaseSeeds):

    def generate_data(
            self,
            prompt: Prompt = None,
    ) -> list[dict]:

        seed_intel_class = django_to_pydantic_model(
            model_class=self.model_class,
            base_class=BaseIntel,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields
        )

        class SeedingIntel(BaseIntel):
            items: list[seed_intel_class]

            def __iter__(self):
                return iter(self.items)

        prompt = (
            Prompt()
            .prompt(prompt)
            .heading('Seed Count')
            .text(f'Create {self.count} {self.model_class.__name__}')

        )

        return LlmSeedingBot.process(
            prompt=prompt,
            intel_class=SeedingIntel
        )


class ModelFakerSeeds(ModelBaseSeeds):

    def generate_data(self) -> list[dict]:
        faker_data = []
        for _ in range(self.count):
            model_data = {}

            for field in self.include_fields:
                model_data[field] = fake_model_field_value(
                    model_class=self.model_class,
                    field_name=field,
                    faker_method=context,
                )
            faker_data.append(model_data)

        return faker_data


class ModelStaticSeeds(ModelBaseSeeds):

    def generate_data(self) -> list[dict]:
        return [{
            field_name: static_data
        } for _ in range(self.count)]


class ModelCallableSeeds(ModelBaseSeeds):

    def generate_data(self) -> list[dict]:
        return [{
            field_name: callable()
        } for _ in range(self.count)]
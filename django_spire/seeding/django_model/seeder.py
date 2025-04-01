from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Type
from itertools import zip_longest
import uuid

from dandy.llm import Prompt
from dandy.intel import BaseIntel

from django_spire.core.converters import django_to_pydantic_model, fake_model_field_value
from django_spire.seeding.django_model.interface import DjangoModelSeederFieldInterface
from django_spire.seeding.intelligence.bots import LlmSeedingBot
from django_spire.seeding.seeder import BaseSeeder

from django.db.models.base import Model


class BaseDjangoModelSeeder(ABC, BaseSeeder, DjangoModelSeederFieldInterface):
    model_class: Type[Model]


class DjangoModelLlmSeeder(BaseDjangoModelSeeder):
    keyword = 'llm'

    @classmethod
    def generate_data(cls, count: int = 1,) -> list[dict]:

        include_fields = list(cls.seeder_fields().keys())

        seed_intel_class = django_to_pydantic_model(
            model_class=cls.model_class,
            base_class=BaseIntel,
            include_fields=include_fields
        )

        class SeedingIntel(BaseIntel):
            items: list[seed_intel_class]

            def __iter__(self):
                return iter(self.items)

        prompt = (
            Prompt()
            .prompt(cls.prompt)
            .heading('Seed Count')
            .text(f'Create {count} {cls.model_class.__name__}')
        )

        intel_data = LlmSeedingBot.process(
            prompt=prompt,
            intel_class=SeedingIntel
        )

        return intel_data


class DjangoModelFakerSeeder(BaseDjangoModelSeeder):
    keyword = 'faker'

    @classmethod
    def seed(cls, count = 1) -> list[dict]:
        data = []
        for i in range(count):
            row = {}
            for field_name, faker_config in cls.seeder_fields().items():
                faker_method = faker_config[1:] if len(faker_config) > 1 else None
                row[field_name] = fake_model_field_value(
                    model_class=cls.model_class,
                    field_name=field_name,
                    faker_method=faker_method
                )
            data.append(row)
        return data

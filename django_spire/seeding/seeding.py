from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import zip_longest

from django.db.models.base import Model
from typing import Type

from dandy.llm import Prompt
from dandy.intel import BaseIntel

from django_spire.core.converters import django_to_pydantic_model, fake_model_field_value


class ModelSeeding:

    def __init__(
            self,
            model_class: Type[Model],
            fields: dict[str, tuple] = None,
            prompt: Prompt = None,
            include_fields: list[str] = None,
            exclude_fields: list[str] = None
    ):
        self.model_class = model_class
        self.prompt = prompt or Prompt()

        self._validate_fields_exist(fields)
        self.fields = self._normalize_fields(fields)

        self.exclude_fields = exclude_fields or []
        self.include_fields = include_fields or []

        self._assign_default_llm_fields()

    def _normalize_fields(self, fields: dict | None) -> dict:

        if fields is None:
            fields = {}

        seed_keywords = {"faker", "llm", "static", "callable", "custom"}
        normalized = {}
        for k, v in fields.items():
            if isinstance(v, tuple):
                normalized[k] = v
            elif callable(v):
                normalized[k] = ("callable", v)
            elif isinstance(v, str) and v.lower() in seed_keywords:
                normalized[k] = (v.lower(),)
            else:
                normalized[k] = ("static", v)
        return normalized

    def _validate_fields_exist(self, fields: dict):
        model_fields = {field.name for field in self.model_class._meta.fields}
        unknown = set(fields.keys()) - model_fields
        if unknown:
            raise ValueError(f"Invalid field name(s): {', '.join(unknown)}")

    def _assign_default_llm_fields(self):
        used_fields = set(self.fields.keys()) | set(self.exclude_fields)
        all_field_names = [f.name for f in self.model_class._meta.fields if f.name not in used_fields]
        llm_fields = {field_name: ('llm',) for field_name in all_field_names}
        self.fields.update(llm_fields)

    def filter_fields(self, seed_type: str) -> dict:
        matched_fields = {}
        for key, value in self.fields.items():
            if not isinstance(value, tuple):
                value = (value,)
            if value and value[0] == seed_type:
                matched_fields[key] = self.fields[key]
        return matched_fields

    def _callable_seed_data(self, count=1) -> list[dict]:
        callable_fields = self.filter_fields('callable')
        return ModelCallableSeeds(
            model_class=self.model_class,
            fields=callable_fields,
            count=count
        ).generate_data()

    def _faker_seed_data(self, count=1) -> list[dict]:
        faker_fields = self.filter_fields('faker')
        return ModelFakerSeeds(
            model_class=self.model_class,
            fields=faker_fields,
            count=count
        ).generate_data()

    def _llm_seed_data(self, count=1) -> list[dict]:
        if any(len(info) > 1 for info in self.fields.values() if info[0] == 'llm'):
            field_prompt = (
                Prompt()
                .heading('Fields Context Data')
                .list([
                    f'{name}: {info[1]}'
                    for name, info in self.fields.items()
                    if info[0] == 'llm' and len(info) > 1
                ])
            )
            self.prompt = self.prompt.prompt(field_prompt)

        llm_fields = self.filter_fields('llm')

        return ModelLlmSeeds(
            model_class=self.model_class,
            fields=llm_fields,
            count=count
        ).generate_data(
            prompt=self.prompt
        )

    def _static_seed_data(self, count=1) -> list[dict]:
        static_fields = self.filter_fields('static')
        return ModelStaticSeeds(
            model_class=self.model_class,
            fields=static_fields,
            count=count
        ).generate_data()

    def _custom_seed_data(self, count=1) -> list[dict]:
        custom_fields = self.filter_fields('custom')
        return ModelCustomSeeds(
            model_class=self.model_class,
            fields=custom_fields,
            count=count
        ).generate_data()

    def seed_data(self, count=1) -> list[dict]:
        llm_seed_data = self._llm_seed_data(count)
        faker_seed_data = self._faker_seed_data(count)
        static_seed_data = self._static_seed_data(count)
        callable_seed_data = self._callable_seed_data(count)

        return [
            {**(d1 or {}), **(d2 or {}), **(d3 or {}), **(d4 or {}), **(d5 or {})}
            for d1, d2, d3, d4, d5 in zip_longest(llm_seed_data, faker_seed_data, static_seed_data, callable_seed_data, self._custom_seed_data(count))
        ]

    def generate_model_objects(
            self,
            count: int = 1,
            fields: dict | None = None,
            clear_cache: bool = False
    ):
        # Todo: Need to implement caching.
        original_fields = self.fields.copy()

        if fields:
            self._validate_fields_exist(fields)
            self.fields = self._normalize_fields({**original_fields, **fields})
            self._assign_default_llm_fields()

        model_objects = [self.model_class(**seed_data) for seed_data in self.seed_data(count)]

        self.fields = original_fields
        return model_objects

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
            fields: dict,
            count: int = 1
    ):
        self.model_class = model_class
        self.fields = fields
        self.count = count

    @abstractmethod
    def generate_data(self, *args, **kwargs):
        pass


class ModelLlmSeeds(ModelBaseSeeds):

    # @cache_to_sqlite('seeding')
    def generate_data(
        self,
        prompt: Prompt = None
    ) -> list[dict]:

        include_fields = list(self.fields.keys())
        seed_intel_class = django_to_pydantic_model(
            model_class=self.model_class,
            base_class=BaseIntel,
            include_fields=include_fields,
            exclude_fields=[]
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

        from django_spire.seeding.intelligence.bots import LlmSeedingBot

        intel_data = LlmSeedingBot.process(
            prompt=prompt,
            intel_class=SeedingIntel
        )

        return intel_data


class ModelFakerSeeds(ModelBaseSeeds):

    # @cache_to_sqlite('seeding')
    def generate_data(self) -> list[dict]:
        data = []
        for i in range(self.count):
            row = {}
            for field_name, faker_config in self.fields.items():
                faker_method = faker_config[1:] if len(faker_config) > 1 else faker_config[0]
                row[field_name] = fake_model_field_value(
                    model_class=self.model_class,
                    field_name=field_name,
                    faker_method=faker_method
                )
            data.append(row)
        return data


class ModelStaticSeeds(ModelBaseSeeds):

    # @cache_to_sqlite('seeding')
    def generate_data(self) -> list[dict]:
        return [
            {field_name: value[0] for field_name, value in self.fields.items()}
            for _ in range(self.count)
        ]


class ModelCustomSeeds(ModelBaseSeeds):

    def in_order(self, values: list, index: int) -> any:
        if index >= len(values):
            raise IndexError("Index exceeds the list length in 'in_order'")
        return values[index]

    # @cache_to_sqlite('seeding')
    def generate_data(self) -> list[dict]:
        data = []
        for i in range(self.count):
            row = {}
            for field_name, config in self.fields.items():
                method_name = config[1] if len(config) > 1 else field_name
                kwargs = config[2] if len(config) > 2 else {}
                method = getattr(self, method_name, None)

                if not callable(method):
                    raise ValueError(f"Custom method '{method_name}' not found for field '{field_name}'")

                if method_name == "in_order":
                    kwargs["index"] = i

                row[field_name] = method(**kwargs)

            data.append(row)
        return data


class ModelCallableSeeds(ModelBaseSeeds):

    # @cache_to_sqlite('seeding')
    def generate_data(self) -> list[dict]:
        return [
            {field_name: func[0]() for field_name, func in self.fields.items()}
            for _ in range(self.count)
        ]

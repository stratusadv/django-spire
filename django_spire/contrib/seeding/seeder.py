import json
import re
import time
from typing import Any, TYPE_CHECKING

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import QuerySet

from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.helper.custom_helper import CustomFieldSeedHelper
from django_spire.contrib.seeding.field.seed.helper.fake_helper import FakeFieldSeedHelper
from django_spire.contrib.seeding.field.seed.helper.model_helper import ModelFieldSeedHelper
from django_spire.contrib.seeding.field.seed.helper.random_helper import RandomFieldSeedHelper
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.seed.factory.factory import SeedFactory
from django_spire.contrib.seeding.seed.factory.model_factory import ModelSeedFactory

if TYPE_CHECKING:
    from django_spire.contrib.seeding.seed.seed import Seed


class Seeder:
    locale: str | list[str] = 'en_CA'

    custom = CustomFieldSeedHelper(locale)
    fake = FakeFieldSeedHelper(locale)
    model = ModelFieldSeedHelper(locale)
    random = RandomFieldSeedHelper(locale)

    cache_enabled = True

    model_class: type[models.Model] | None = None

    fields_seeds: dict[str, BaseFieldSeed]

    def __init__(self, count: int = 1, verbose: bool = True) -> None:
        self.seeds: list[Seed] = []
        self._model_object_ids: list[int | str] = []
        self._count: int = count
        self.verbose: bool = verbose

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        if cls.fields_seeds is None:
            message = f'{cls.__name__}.fields_seeds is None and must be defined'
            raise ValueError(message)

    @property
    def _cache_name(self) -> str:
        return f'{self.__class__.__name__.lower()}_cache'

    @property
    def name_verbose(self) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', self.__class__.__name__)

    @property
    def queryset(self) -> QuerySet[models.Model]:
        if self.model_class is None:
            message = 'Cannot create queryset without a model class'
            raise DjangoSpireSeederError(message)

        return self.model_class.objects.filter(pk__in=self._model_object_ids)

    @staticmethod
    def exclude() -> ExcludeFieldSeed:
        return ExcludeFieldSeed()

    @staticmethod
    def static(value: Any) -> StaticFieldSeed:
        return StaticFieldSeed(value)

    @classmethod
    def llm(cls, field_type: type, prompt: str | None = None) -> LlmFieldSeed:
        return LlmFieldSeed(field_type=field_type, prompt=prompt, locale=cls.locale)

    def __post_seed__(self) -> None:
        pass

    def __post_seed_database__(self) -> None:
        pass

    def seed(self, count: int | None = None) -> None:
        seed_count = self._count if count is None else count

        if not self.seeds:
            start_time = time.perf_counter()

            self._print_seeder_start(seed_count)

            if self.model_class is None:
                self.seeds = SeedFactory(seeder=self).generate_seeds(
                    count=seed_count, cache_enabled=self.cache_enabled, cache_name=self._cache_name
                )

            else:
                self.seeds = ModelSeedFactory(seeder=self).generate_seeds(
                    count=seed_count, cache_enabled=self.cache_enabled, cache_name=self._cache_name
                )

            self._print_post(spacing=4)

            self.__post_seed__()

            self._print_completed(start_time)

    def seed_class(self, class_: type, count: int | None = None) -> list[type]:
        self.seed(count)

        return [class_(**fields_values) for fields_values in self.to_list_of_dicts()]

    def seed_database(self, count: int | None = None) -> QuerySet:

        if self.model_class is None:
            message = 'Cannot seed database without a model class'
            raise DjangoSpireSeederError(message)

        self.seed(count)

        start_time = time.perf_counter()

        self._print_saving_to_database()

        model_objects = self.model_class.objects.bulk_create(
            objs=self.to_model_instances(), batch_size=1000
        )

        self._model_object_ids = [model_object.id for model_object in model_objects]

        self._print_post(spacing=7)

        self.__post_seed_database__()

        self._print_completed(start_time)

        return self.queryset

    def _print_completed(self, start_time: float) -> None:
        if self.verbose:
            print('\b' * 4 + ' ' * 4 + '\b' * 4, end='', flush=True)
            completed_time = time.perf_counter() - start_time
            if completed_time >= 2.0:
                print(f'Completed in \033[31m{completed_time:6.2f}s\033[0m')
            else:
                print(f'Completed in {completed_time:6.2f}s')

    def _print_post(self, spacing: int) -> None:
        if self.verbose:
            print('\b' * spacing + ' ' * spacing + '\b' * spacing, end='', flush=True)
            print('Post', end='', flush=True)

    def _print_saving_to_database(self) -> None:
        if self.verbose:
            print(f' -> Saving to Database {"." * 13} Waiting', end='', flush=True)

    def _print_seeder_start(self, seed_count: int) -> None:
        if self.verbose:
            print(f'\n\033[34m{self.name_verbose}\033[0m')
            print(f' -> Seeding > {seed_count:6} > ', end='', flush=True)

    def reseed_database(self, count: int | None = None) -> QuerySet:
        self.reset()
        return self.seed_database(count=count)

    def reseed(self, count: int | None = None) -> None:
        self.reset()
        self.seed(count=count)

    def reset(self) -> None:
        self.seeds.clear()
        self._model_object_ids.clear()

    def to_json(self, count: int | None = None) -> str:
        self.seed(count=count)

        if self.model_class is not None:
            return serializers.serialize('json', self.queryset)

        return json.dumps(self.seeds, cls=DjangoJSONEncoder)

    def to_list_of_dicts(self, count: int | None = None) -> list[dict[str, Any]]:
        self.seed(count=count)

        return [seed.to_dict() for seed in self.seeds]

    def to_model_instances(self, count: int | None = None) -> list[models.Model]:
        if self.model_class is None:
            message = 'Cannot create models instances without a model class'
            raise DjangoSpireSeederError(message)

        self.seed(count=count)

        return [self.model_class(**fields_values) for fields_values in self.to_list_of_dicts()]

    def _validate(self) -> None:
        for field, seed in self.fields_seeds.items():
            if not isinstance(field, str):
                message = f'{self.__class__.__name__}.fields_seeds keys must all be strings'
                raise DjangoSpireSeederError(message)

            if not isinstance(seed, BaseFieldSeed):
                message = f'{self.__class__.__name__}.fields_seeds keys must all be BaseFieldSeed'
                raise DjangoSpireSeederError(message)

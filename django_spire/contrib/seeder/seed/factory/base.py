from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from dandy import generate_cache_key, SqliteCache
from django_spire.contrib.seeder.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeder.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeder.seed.seed import Seed

if TYPE_CHECKING:
    from django_spire.contrib.seeder import Seeder


class BaseSeedFactory(ABC):
    def __init__(self, seeder: Seeder) -> None:
        self.seeder = seeder
        self._validate()

    def _generate_seed(self) -> Seed:
        return Seed({**self._process_llm_fields(**self._process_non_llm_fields())})

    def _generate_seeds(self, count: int) -> list[Seed]:
        return [self._generate_seed() for _ in range(count)]

    def generate_seeds(self, count: int, cache_enabled: bool, cache_name: str) -> list[Seed]:
        seeds = None

        if cache_enabled:
            cache_key = generate_cache_key(
                self._generate_seeds, self.seeder.fields_seeds, count=count
            )

            cache = SqliteCache(cache_name=cache_name, limit=100)
            seeds: list[Seed] | None = cache.get(cache_key)

            if seeds:
                return seeds

            seeds = self._generate_seeds(count)

            cache.set(cache_key, seeds)

        if seeds is None:
            seeds = self._generate_seeds(count)

        return seeds

    def _process_llm_fields(self, fields_values: dict[str, Any]) -> dict[str, Any]:
        for field, seed in self.seeder.fields_seeds.items():
            if isinstance(seed, LlmFieldSeed):
                fields_values[field] = 'FUTURE GOES HERE'

        return fields_values

    def _process_non_llm_fields(self) -> dict[str, Any]:
        fields_values = {}

        for field, seed in self.seeder.fields_seeds.items():
            if not isinstance(seed, ExcludeFieldSeed) and not isinstance(seed, LlmFieldSeed):
                fields_values[field] = seed.generate_value()

        return fields_values

    @abstractmethod
    def _validate(self) -> None:
        raise NotImplementedError

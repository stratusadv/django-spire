from __future__ import annotations

import time
from abc import ABC, abstractmethod
from time import sleep
from typing import TYPE_CHECKING, Any

from dandy import generate_cache_key, SqliteCache

from django_spire.contrib.seeder.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeder.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeder.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeder.intelligence.bots.field_seeding_bot import FieldSeedingBot

if TYPE_CHECKING:
    from django_spire.contrib.seeder.seed.seed import Seed
    from django_spire.contrib.seeder import Seeder


class BaseSeedFactory(ABC):
    def __init__(self, seeder: Seeder) -> None:
        self.seeder = seeder
        self._validate()

    def _generate_seeds(self, count: int) -> list[Seed]:
        futures = []
        seeds: list[Seed] = []

        if self.seeder.verbose:
            print(f'{0:3}%', end='', flush=True)

        for i in range(count):
            futures.append(
                FieldSeedingBot().process_to_future(
                    seeder_name=self.seeder.name_verbose, fields_seeds=self.seeder.fields_seeds
                )
            )

            if self.seeder.verbose:
                progress = int(((i + 1) / count) * 100)
                if progress % 5 == 0:
                    print('\b' * 4 + ' ' * 4 + '\b' * 4, end='', flush=True)
                    print(f'{progress:3}%', end='', flush=True)

            if len(futures) >= 15 or i == count - 1:
                seeds.extend([future.get_result(timeout_seconds=10) for future in futures])
                futures = []

        if len(seeds) != count:
            message = f'Failed to generate enough seeds, generated {len(seeds)} or {count} required'
            raise DjangoSpireSeederError(message)

        return seeds

    def generate_seeds(self, count: int, cache_enabled: bool, cache_name: str) -> list[Seed]:
        if cache_enabled:
            cache_key = generate_cache_key(
                self._generate_seeds, self.seeder.fields_seeds, count=count
            )

            cache = SqliteCache(cache_name=cache_name, limit=100)
            cached_seeds: list[Seed] | None = cache.get(cache_key)

            if cached_seeds:
                if self.seeder.verbose:
                    print(f'Cached {"." * 3}{" " * 4} ', end='', flush=True)

                return cached_seeds

        if self.seeder.verbose:
            print(f'Fresh {"." * 4} ', end='', flush=True)

        fresh_seeds = self._generate_seeds(count)

        if cache_enabled:
            cache.set(cache_key, fresh_seeds)  # noqa

        return fresh_seeds

    @abstractmethod
    def _validate(self) -> None:
        raise NotImplementedError

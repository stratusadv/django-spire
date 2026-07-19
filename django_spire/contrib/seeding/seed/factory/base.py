from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from dandy import DandyRecoverableError, SqliteCache, generate_cache_key

from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.intelligence.bots.field_seeding_bot import FieldSeedingBot

if TYPE_CHECKING:
    from django_spire.contrib.seeding import Seeder
    from django_spire.contrib.seeding.seed.seed import Seed


class BaseSeedFactory(ABC):
    def __init__(self, seeder: Seeder) -> None:
        self.seeder = seeder
        self.current_progress = 0
        self._validate()

    def _generate_seeds(self, count: int) -> list[Seed]:
        futures = []
        seeds: list[Seed] = []

        for i in range(count):
            if i == 0:
                self._run_init_seed()

            futures.append(
                FieldSeedingBot().process_to_future(
                    seeder_name=self.seeder.name_verbose,
                    fields_seeds=self.seeder.fields_seeds,
                    seed_index=i,
                )
            )

            self._print_progress(i, count)


            if len(futures) >= 13 or i == count - 1:
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
                self._print_cached()

                self.seeder.meta.cached_seed_count += count

                return cached_seeds

        self._print_fresh()

        try:
            fresh_seeds = self._generate_seeds(count)
        except DandyRecoverableError:
            self._print_retry()
            fresh_seeds = self._generate_seeds(count)

        if cache_enabled:
            cache.set(cache_key, fresh_seeds)

        self.seeder.meta.fresh_seed_count += count

        return fresh_seeds

    def _run_init_seed(self) -> None:
        self._print_init()

        FieldSeedingBot().process(
            seeder_name=self.seeder.name_verbose,
            fields_seeds=self.seeder.fields_seeds,
            seed_index=-1,
        )

    def _print_cached(self) -> None:
        if self.seeder.verbose:
            print(f'\033[35mCached\033[0m {"." * 6}{" " * 4} ', end='', flush=True)

    def _print_fresh(self) -> None:
        if self.seeder.verbose:
            print(f'\033[32mFresh\033[0m {"." * 7} ', end='', flush=True)

    def _print_progress(self, index: int, count: int) -> None:
        if self.seeder.verbose:
            progress = int(((index + 1) / count) * 100)

            if progress != self.current_progress:
                print('\b' * 4 + ' ' * 4 + '\b' * 4, end='', flush=True)
                print(f'{progress:3}%', end='', flush=True)

            self.current_progress = progress

    def _print_retry(self) -> None:
        if self.seeder.verbose:
            print('\b' * 4 + ' ' * 4 + '\b' * 4, end='', flush=True)
            print('\033[31mRetry\033[0m ', end='', flush=True)

    def _print_init(self) -> None:
        if self.seeder.verbose:
            print(f'Init', end='', flush=True)

    @abstractmethod
    def _validate(self) -> None:
        raise NotImplementedError

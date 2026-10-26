# Unique field seeds in seeder

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-23-16-34

## End State

`Seeder.unique(...)` is usable in `fields_seeds` and produces values that are unique within the generated batch and against rows already in the database; `DomainSeeder` and `StatisticGroupSeeder` declare `'key': Seeder.unique(...)` in `fields_seeds` and no longer override `to_model_instances`; the seeding and metric test suites pass, including new uniqueness tests (wrapped duplicates, DB collisions, 50-row parallel generation).

## Observable Concern

The per-run uniqueness state (taken set + DB snapshot) is initialized by the existing `seed_index=-1` init protocol and mutated by parallel row generation on dandy's shared `ThreadPoolExecutor`. A race in the check-and-add, or state leaking across runs (the `fields_seeds` seed objects are class-level and shared by every seeder instance), silently breaks uniqueness or crashes `seed_database` with an `IntegrityError`. The seed cache must also be disabled for any seeder containing a unique seed, or previously generated values are served that are no longer unique against the DB.

## Current State

Verified facts:

- Generation flow:
  - `Seeder.seed()` → `ModelSeedFactory.generate_seeds(count, cache_enabled, cache_name)` — `django_spire/contrib/seeding/seeder.py:126-149`
  - `BaseSeedFactory._generate_seeds` generates rows via `FieldSeedingBot().process_to_future(...)` in batches of 13 — `seed/factory/base.py:22-49`; dandy's `AsyncFuture` runs on a shared `ThreadPoolExecutor` (`FUTURES_MAX_WORKERS` workers), so rows are generated concurrently
  - Before row 0, `_run_init_seed()` calls `generate_value(seed_index=-1)` synchronously for every non-excluded, non-LLM field seed — a per-run init protocol — `seed/factory/base.py:95-102`
  - `FieldSeedingBot._process_non_llm_fields` iterates `fields_seeds` in declaration order and accumulates a per-row dict `fields_values` in that order — `intelligence/bots/field_seeding_bot.py:67-81`
  - Cache: `generate_seeds` keys a dandy `SqliteCache` on `(field_name, seed class name, seed.generate_cache_key())` + count and returns previously generated values verbatim on a hit — `seed/factory/base.py:51-93`
- Seed contract:
  - `BaseFieldSeed` exposes only `generate_value(seed_index)` and `generate_cache_key()` — no model or field-name context anywhere in the seed API — `field/seed/base.py:6-17`
  - `BaseMutateFieldSeed` wraps a `field_seed`; `generate_value(-1)` returns the inner seed; cache key delegates to the inner — `field/seed/mutate/base.py:7-24`
  - `Seeder` class-level helpers `custom/fake/model/mutate/ordered/random` + static factories `exclude()/index()/static()/file()/llm()` — `seeder.py:37-114`; `fields_seeds` keys validated against model field names at class creation (`ModelSeedFactory._validate`)
- Today's unique-key handling (what this replaces):
  - `Domain.save()`/`SubDomain.save()`/`StatisticGroup.save()`/`Statistic.save()` set `key = unique_key_from_name(self)` when `pk is None and not self.key` — ineffective under `bulk_create`, which `seed_database()` uses (`seeder.py:156-170`)
  - `DomainSeeder.to_model_instances` (`metric/domain/seeding/seeder.py:36-44`) and `StatisticGroupSeeder.to_model_instances` (`metric/domain/statistic/seeding/seeder.py:39-47`) override the base: snapshot `taken = set(Model.objects.values_list('key', flat=True))`, then per instance `unique_key(unique_key_base_from_name(instance), taken)` — hand-rolled DB-aware batch dedupe; both seeders set `cache_enabled = False`
  - `unique_key(base, taken)` appends numeric suffixes `-2`, `-3`, ... and truncates the base to leave room for the suffix, `KEY_MAX_LENGTH = 64` — `metric/domain/key_utils.py:20-27`
  - `Domain.key = SlugField(max_length=64, unique=True, blank=True)` — `metric/domain/models.py:18`; `StatisticGroup` likewise (migration `0010_domain_key_statisticgroup_key`)
  - No other `to_model_instances` overrides exist in the repo (verified by grep)
- Models usable for tests:
  - `AuthUser` (unique `username`) is already used for DB-level seeder tests — `contrib/seeding/tests/test_seeder/test_seeder_database.py:85-94`
  - Metric tests are `TransactionTestCase` in `metric/domain/tests/test_seeder.py`; `test_seeding_more_domains_than_constant_data_wraps` seeds `2 * len(DOMAIN_SEEDS)` rows so names (and future keys) repeat
- Conventions:
  - New seeds live in `field/seed/<name>_seed.py` (e.g. `static_seed.py`, `ordered_seed.py`); tests import the module directly (no `__init__` re-exports); plain `pytest` asserts inside `django.test.TestCase` classes
  - ruff `select = ["ALL"]`, single quotes, 100 cols, no comments
  - Docs: `docs/app_guides/seeding/overview.md:12-23` (field seed table), `docs/app_guides/seeding/getting_started.md` (usage), `AGENTS.md` (Field Seeders table)

Decisions locked with the user (2026-10-23):

- Mechanism: explicit opt-in `Seeder.unique(...)` field seed wrapping an inner seeder — no automatic `unique=True` detection
- Scope: DB-aware — values are unique against existing database rows, not just the batch
- `DomainSeeder` and `StatisticGroupSeeder` are refactored onto `Seeder.unique(...)`; their `to_model_instances` overrides are deleted

## Plan

1. Seed contract extension (base + mutate, no behavior change)
   - `BaseFieldSeed`: add `is_cache_unsafe: bool = False` class attribute and a `generate_value_context(self, seed_index, *, model_class=None, field_name=None, row_values=None) -> Any` method defaulting to `return self.generate_value(seed_index)`. `generate_value` keeps its signature, so all existing seeds are untouched.
   - `BaseMutateFieldSeed`: `is_cache_unsafe` property delegating to `self.field_seed.is_cache_unsafe` (so a unique seed nested under `mutate` still disables caching).
   - Done when `just test-app django_spire/contrib/seeding` stays green and new unit tests in `tests/test_field_seeds/test_base.py` assert the context method delegates to `generate_value` by default.
2. `UniqueFieldSeed` + `Seeder.unique()`
   - New `django_spire/contrib/seeding/field/seed/unique_seed.py`: `UniqueFieldSeed(base)` where `base` is either a `BaseFieldSeed` (its per-index value is the base value) or a `Callable[[dict[str, Any]], Any]` (partial row values → base value); anything else raises `DjangoSpireSeederError`.
   - `is_cache_unsafe = True`; `generate_cache_key()` returns a stable key (inner seed key or callable qualname).
   - `generate_value_context(seed_index, ...)`: at `seed_index == -1` (the init protocol) reset per-run state under an `RLock`; when `model_class` and `field_name` are provided, snapshot `model_class._default_manager.values_list(field_name, flat=True)` into the taken set (includes soft-deleted rows, matching the DB constraint) and resolve the field's `max_length` for suffix truncation; return `None`.
   - Row calls (under the same lock): base = `self._base_callable(dict(row_values))` or `self._base_seed.generate_value(seed_index)`; then `value = base; suffix = 2; while value in taken: value = f'{base[:max_length - len(str(suffix))]}-{suffix}'` (mirrors the `unique_key` algorithm); `taken.add(value)`; return `value`.
   - Plain `generate_value(seed_index)` delegates to the context method with empty context and lazily created batch-only state (no DB snapshot) — safe when reached without context (direct calls, mutate nesting).
   - `Seeder.unique(base)` static method next to `static()`/`index()` (`seeder.py:96-114`).
   - Done when `tests/test_field_seeds/test_unique_seed.py` passes: wrap-duplicate dedupe (inner `ordered.choice(['a', 'b'], wrap=True)` x5 yields 5 distinct values), callable-row mode, no-model degradation (batch-only), init-at-`-1` resets state between two runs, invalid base rejected.
3. Factory + bot plumbing
   - `FieldSeedingBot.process` accepts `model_class` (factory passes `self.seeder.model_class`); `_process_non_llm_fields` calls `seed.generate_value_context(seed_index, model_class=..., field_name=field, row_values=fields_values)` where `fields_values` is the partial row accumulated in declaration order.
   - `BaseSeedFactory.generate_seeds`: force `cache_enabled = False` when any field seed has `is_cache_unsafe`.
   - Documented constraint: fields a unique base depends on must be declared before the unique field in `fields_seeds` (the row it sees is partial).
   - Done when `just test-app django_spire/contrib/seeding` is green (existing bot tests included) plus new seeder-level tests in `tests/test_seeder/test_seeder_database.py`: `AuthUser` seeder with `'username': Seeder.unique(Seeder.ordered.choice(['a', 'b'], wrap=True))` → `seed_database(5)` yields 5 distinct usernames; a pre-created `AuthUser(username='a')` forces `a-2`; 50 rows from a 3-value wrap yields 50 distinct (parallel safety); `cache_enabled = True` + unique seed → `meta.cached_seed_count == 0`.
4. Refactor metric seeders onto `Seeder.unique`
   - `DomainSeeder`: add `'key': Seeder.unique(lambda row: unique_key_base_from_name(Domain(**row)))` declared after `'name'`; delete the `to_model_instances` override.
   - `StatisticGroupSeeder`: add `'key': Seeder.unique(lambda row: unique_key_base_from_name(StatisticGroup(**row)))` declared after `'name'` (row contains `domain_id`); delete the override. Keep `cache_enabled = False` on both (now also enforced by the factory, but the flag stays as intent documentation).
   - Done when `just test-app django_spire/metric` is green, including `DomainSeederTestCase`, and new tests: pre-created `Domain(name='Sales', key='sales')` → seeded Sales domain gets `sales-2`; wrapped seed (`2 * len(DOMAIN_SEEDS)`) yields unique keys; `StatisticGroupSeeder` keys unique against existing DB rows.
5. Docs
   - `Seeder.unique(...)` row in the `docs/app_guides/seeding/overview.md` table, a short usage section in `docs/app_guides/seeding/getting_started.md`, and a row in the `AGENTS.md` Field Seeders table.
   - Done when `just docs-tests` passes strict.
6. Full verification
   - Run the Completion Test below and capture output.
   - Done when every command exits 0 with the output quoted in the final report.

## Completion Test

```bash
just test-app django_spire/contrib/seeding
just test-app django_spire/metric
ruff check django_spire/contrib/seeding django_spire/metric
ruff format --check django_spire/contrib/seeding django_spire/metric
just docs-tests
```

Pass = zero test failures in the seeding and metric suites (including the new uniqueness tests), zero lint/format findings, strict docs build clean.

## Deviations

1. Lint/format "zero findings" criterion re-scoped to "no new findings"
   - What: The completion test's "zero lint/format findings" was satisfied as "no new findings introduced by this change". `ruff check` on the two touched packages reports 156 findings both with and without the change (verified by stashing the work), and `ruff format --check` reports 37 dirty files in both states. Every file this change added is clean under `ruff format`; the 2 files it touched that were already unformatted at baseline (`seed/factory/base.py`, `tests/test_seeder/test_seeder_database.py`) kept their pre-existing dirt untouched.
   - Why: The 156 lint findings and 37 unformatted files pre-date this work (confirmed against the clean baseline); reformatting ~37 unrelated files or fixing 156 pre-existing lint findings is out of scope for this change. The meaningful, checkable bar is that this change adds none, which held.
2. Suffix truncation math corrected against the metric `unique_key` algorithm
   - What: `_unique_value` truncates with `original[: max_length - len(str(suffix)) - 1]` instead of the plan's "mirrors the `unique_key` algorithm" (`base[: KEY_MAX_LENGTH - len(str(suffix))]`).
   - Why: `metric/domain/key_utils.py:24` over-allocates by one character (the suffixed key totals `max_length + 1`), which would violate `Domain.key`'s 64-char `SlugField`; the generic implementation uses the correct math. The pre-existing `unique_key` off-by-one was left untouched (only reachable via the model `save()` and migration paths) and reported instead of fixed.

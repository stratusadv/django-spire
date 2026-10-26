# Unique-seed audit of remaining seeders

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-23-19-08

## End State

Every production seeder that seeds a `unique=True` model field generates values unique within the batch and against pre-existing database rows, proven by non-AI tests for each affected seeder.

## Observable Concern

`Signage.key` is a `UUIDField`, and `UniqueFieldSeed`'s numeric-suffix collision strategy produces strings that are not valid UUIDs - a unique-wrapped UUID field would trade an `IntegrityError` for a `DataError`, so that seeder needs a different mechanism than the three string-key seeders.

## Current State

Audit of all 91 `Seeder` subclasses against every model unique constraint (`unique=True`, `UniqueConstraint`, `unique_together`):

- Already safe: `UserSeeder` (`username` via `Seeder.unique('email')`), `DomainSeeder`/`StatisticGroupSeeder` (key via `Seeder.unique(lambda ...)`), `PirateModelSeeder` (`username` via `uuid4` provider), all composite `UniqueConstraint`s (explicit per-parent `order`), and runtime-generated uniques with no seeder (`CeleryTask.task_id`, `CelerySchedulerTask.schedule_key`, `CeleryTaskSweep.key`, `Mfa.code`, `SmsTemporaryMedia.external_access_key`, `SmsUser.phone_number`, `Tag.name`).
- Gap (4 metric seeders seeding unique keys with `ordered.choice(..., wrap=True)`, no DB awareness):
  - `SubDomainSeeder.key` - `django_spire/metric/domain/seeding/seeder.py:39`
  - `StatisticSeeder.key` - `django_spire/metric/domain/statistic/seeding/seeder.py:52`
  - `VisualRegionSeeder.key` - `django_spire/metric/visual/seeding/seeder.py:182`
  - `SignageSeeder.key` - `django_spire/metric/visual/signage/seeding/seeder.py:19`
- Production runs are safe today: each entrypoint seeds `count == len(curated keys)`, key lists verified 100% unique (13/12/2/8 entries), `SEEDING_MULTIPLIER=1.0`, fresh DB.
- Failure modes: re-seed onto an existing DB (`just seed` twice) and `SEEDING_MULTIPLIER > 1.0` both crash these four with duplicate-key `IntegrityError` while the already-fixed seeders survive by suffixing.
- `SIGNAGE_SEEDS` curated UUIDs are referenced only by the seeder and one test assertion; display URLs are built from DB rows, not constants.
- User chose option 1 (wrap in `Seeder.unique`) from the presented options (wrap / leave as-is / idempotent skip mode).

## Plan

1. Wrap the three string-key seeders
   - `SubDomainSeeder`, `StatisticSeeder`, `VisualRegionSeeder`: `'key': Seeder.unique(Seeder.ordered.choice(..., wrap=True))`.
   - Done when re-seed and over-count runs produce suffixed, unique keys.
2. Fix the UUID key with a valid-UUID mechanism
   - `SignageSeeder.key` -> `Seeder.fake.uuid4()` (Faker-backed, unique per row); remove the now-dead curated UUIDs from `SIGNAGE_SEEDS`.
   - Done when re-seeding signage yields 2N valid, unique UUIDs.
3. Add tests
   - Domain test file: SubDomain wrap + reseed cases; new `StatisticSeederTestCase` with wrap + reseed cases.
   - Visual test file: VisualRegion reseed case.
   - Signage test file: curated-uuid assertion replaced with valid+unique assertion; reseed case.
   - Done when the metric suite passes with the new cases.
4. Lint/format parity
   - `ruff check django_spire/contrib/seeding django_spire/metric` stays at the 156-finding baseline; touched files format-clean.
   - Done when the scoped count reads 156 and every touched file passes `ruff format --check`.

## Completion Test

```bash
just test-app django_spire/metric
ruff check django_spire/contrib/seeding django_spire/metric
ruff format --check <touched files>
just test
```

Observed (2026-10-23 19:1x):

- metric suite: `653 passed, 1 warning, 4 subtests passed in 24.58s` (647 before, +6 new cases)
- `ruff check django_spire/contrib/seeding django_spire/metric`: `Found 156 errors` - exactly the recorded baseline, zero new; all 8 touched files format-clean
- full `just test`: `19 failed, 4779 passed, 2 warnings, 4 subtests passed in 125.34s` - the 19 failures are the identical pre-existing `django_spire/core/components` test_form/test_scroll `Glue.Sequence` set; pass delta reconciles exactly: a HEAD worktree collects 4750 tests, the working tree collects 4798, and the 48-test difference equals the sum of the tests added across the 8 touched/new test files

## Deviations

1. `SignageSeeder` not wrapped in `Seeder.unique` despite the approved "wrap all four" choice
   - What: `SignageSeeder.key` uses `Seeder.fake.uuid4()`; the curated per-seed UUIDs were removed from `SIGNAGE_SEEDS` and the test that asserted them now asserts valid+unique keys.
   - Why: suffixing a UUID base (`<uuid>-2`) yields a 39-char string Postgres rejects as invalid UUID syntax, so `Seeder.unique` strictly worsens the failure (DataError instead of IntegrityError). A per-row `uuid4` is the smallest mechanism that keeps the column valid and unique under re-seed and multiplier > 1; no code or URL referenced the fixed UUID constants.

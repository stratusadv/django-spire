# Centralize metric key handling on the - / -- scheme

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-26-11-16

## End State

All metric key construction, validation, and name-derivation in `django_spire.metric`
(live code, migrations, API schema, tests, docs) flows through one module,
`django_spire/metric/key_utils.py`, where local keys are lowercase slugs using `-`
between words, stored keys join nesting levels with `--` (replacing `__`),
`unique_key` no longer overflows `KEY_MAX_LENGTH`, and a data migration has rewritten
existing `__` keys in the four key columns to `--`.

## Observable Concern

The stored key is a cross-cutting contract: it is a unique column on four tables, a
`django-ninja` path/payload constraint (`MetricKey`), the remote-installation wire
format, and the value projects put in `DJANGO_SPIRE_METRIC_STATISTIC_KEY` /
`DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY`. Missing one consumer does not raise —
`for_key()` simply finds nothing and the lookup 404s or reports missing — so the risk
is a silent key mismatch, and the migration must rewrite rows without tripping the
per-table unique constraint (two different old keys can only collide on a
pre-existing `--` key, which no current validator allows).

## Current State

Verified 2026-10-26 against the working tree (branch `v1.4.0/metric-registry`, HEAD
`67092c96`):

- `django_spire/metric/domain/key_utils.py` is the only name-derivation module:
  `KEY_MAX_LENGTH = 64`, `unique_key_base_from_name` (parent name + instance name,
  slugified, `[:64]`, then `.replace('_', '-')` — the replace is load-bearing,
  `slugify` keeps `_`), `unique_key` (collision suffix `-{n}` with an off-by-one:
  `base[:64 - len(str(n))] - n` totals **65** chars), `unique_key_from_name`
  (taken-set snapshot via `key__startswith=base`).
- `django_spire/metric/utils.py` is the only `__` builder: `_sub_domain_key`,
  `_statistic_group_key`, `_statistic_key` (f-strings with `__`), plus
  `_validate_spec_key` — rejects `__`, caps length, and
  `_KEY_PATTERN = ^[a-z0-9]+(?:[-_][a-z0-9_]+)*$` **allows underscores** in local keys
  (half of the `_` / `-` mix).
- `specs.py` and `metric.py` import those builders; nothing else constructs stored
  keys. `stored_keys()` and `metric_build`'s orphan pass consume the built keys only.
- Four models carry `key = SlugField(max_length=64, unique=True, blank=True)`
  (`Domain`, `SubDomain`, `StatisticGroup`, `Statistic`) and backfill via
  `unique_key_from_name` in `save()` when unset (`domain/models.py`,
  `domain/statistic/models.py`).
- `domain/statistic/api_v1.py` defines
  `MetricKey = Annotated[str, StringConstraints(max_length=64, pattern=r'^[-a-zA-Z0-9_]+$')]`
  — allows uppercase and underscores — used on `record`, `total`, `summary` endpoints.
- Seeders: `Domain`/`StatisticGroup` keys derive via `unique_key_base_from_name`;
  `SubDomain`/`Statistic` keys come from curated flat lists (`website-traffic`,
  `clicks`, ...). `INTERNAL_TRACKING_STATISTIC_KEY = 'clicks'` and
  `INTERNAL_TRACKING_SUB_DOMAIN_KEY = 'website-traffic'` feed the tracking settings,
  which the user is moving into `test_project/metric_settings.py` **in flight in the
  working tree** (alongside an emptied `django_spire/metric/__init__.py` — no more
  package-level re-exports; `Metric` is imported from `django_spire.metric.metric`).
  This plan builds on those in-flight changes and does not touch them.
- Tests hard-code `__` stored keys: `test_metric_spec.py` (4 literals +
  `test_key_must_be_slug_like`, `test_key_must_not_contain_double_underscore`),
  `test_metric_build.py` (14), `test_metric_remote.py` (7),
  `test_project/app/metrics/tests/test_views.py` (2).
- Docs carry the `__` contract: `docs/app_guides/metric/registry.md` (key table,
  validation list, legacy-key example) and the v1.4.0 `### Added` entry in
  `docs/changelog/changelog.md` (`store__web`, `store__orders__created`).
- Migrations: latest is `0011`; **migration `0010` imports
  `unique_key_from_name` from `django_spire.metric.domain.key_utils` at run time**, so
  deleting that module without updating `0010` breaks fresh databases.
- Out of scope, verified separate identifier spaces: `contrib/rest/schema/schemaset.py`
  (its own `__` path convention), `visual` (flat `VisualRegion.key` CharField; region
  keys use `:`, signage keys are UUIDs), `report` (no key handling),
  `StatisticValue.reference` (`:`-joined), `reference_matches` wildcards.
- Baselines: metric suite 671 passed; full `just test` 4798 passed with 19
  pre-existing `core/components` `Glue.child` shim failures; ruff is the venv binary
  (`line-length = 120`, migrations excluded).

## Plan

1. Central module + its unit tests
   - Create `django_spire/metric/key_utils.py`: `KEY_MAX_LENGTH`, `KEY_WORD_SEPARATOR = '-'`,
     `KEY_OBJECT_SEPARATOR = '--'`, `LOCAL_KEY_PATTERN = ^[a-z0-9]+(?:-[a-z0-9]+)*$`,
     `STORAGE_KEY_PATTERN` (local segments joined by `--`), `object_key(*local_keys)`,
     `validate_local_key(key, kind)` (non-empty str, no `--`, ≤ 64, strict slug — this
     replaces `_validate_spec_key` and rejects `_`), and the moved
     `unique_key_base_from_name` / `unique_key` / `unique_key_from_name` with the
     off-by-one fixed (`base[: KEY_MAX_LENGTH - len(str(suffix)) - 1]`).
   - Create `django_spire/metric/tests/` (matches the per-subpackage `tests/`
     convention used by `domain/`, `visual/`, `report/`) with `test_key_utils.py`:
     object-key building, local validation (uppercase, `_`, `--`, leading/trailing
     `-`, length), storage pattern accept/reject, off-by-one (suffixed 64-char base
     stays ≤ 64), and name-derivation slugifying `_`.
   - Done when `just python -m pytest django_spire/metric/tests --reuse-db -q` passes.
2. Point every consumer at the central module
   - `metric/utils.py`: the three builders return `object_key(...)`; delete
     `_KEY_PATTERN` and `_validate_spec_key`, call `validate_local_key` at the four
     validation sites.
   - `api_v1.py`: `MetricKey` uses `KEY_MAX_LENGTH` and `STORAGE_KEY_PATTERN.pattern`.
   - `domain/models.py`, `domain/statistic/models.py`, both seeding seeders, and
     migration `0010`: import from `django_spire.metric.key_utils`.
   - Delete `django_spire/metric/domain/key_utils.py` (no alias at the old path —
     the feature is unreleased; `0010` is updated in place since it has only ever
     shipped in this branch).
   - Done when `grep -rn 'domain.key_utils\|_KEY_PATTERN\|_validate_spec_key'
     django_spire/` is empty and the metric suite passes.
3. Data migration
   - `0012_metric_key_object_separator` (app label `django_spire_metric_domain`):
     RunPython forward rewrites every `__` in the `key` of `Domain`, `SubDomain`,
     `StatisticGroup`, `Statistic` to `--`, skipping and logging a warning when the
     target key is already taken (unique constraint); reverse rewrites `--` back to
     `__` for the symmetric case.
   - Test by importing the RunPython functions: a `__` row is rewritten, a colliding
     target is skipped, re-running is a no-op.
   - Done when `just migrate` applies it to the dev DB and the migration test passes.
4. Existing tests onto the `--` contract
   - `test_metric_spec.py`: stored-key literals `store--web` etc.;
     `test_key_must_not_contain_double_underscore` becomes the double-hyphen case;
     `test_key_must_be_slug_like` gains the underscore-rejection case.
   - `test_metric_build.py`, `test_metric_remote.py`,
     `test_project/app/metrics/tests/test_views.py`: `__` → `--` literals.
   - Done when `just python -m pytest django_spire/metric test_project/app/metrics
     --reuse-db -n 12 -q` passes.
5. Docs and changelog
   - `registry.md`: key-contract table `store--web` / `store--orders--created`,
     validation list (`--` not allowed, no underscores), legacy example
     `sales--web`; the example import becomes `from django_spire.metric.metric import
     Metric` (the package-level re-export is gone in the working tree).
   - `changelog.md`: new `### Breaking` entry under v1.4.0 (stored-key separator
     `__` → `--` with the migration; spec keys now strict slugs; `MetricKey` API
     pattern tightened; tracking-settings keys must use the stored form) and correct
     the `### Added` registry entry's `store__*` examples.
   - Done when `just docs-tests` builds clean.
6. Full verification
   - `just test`; `just make-migrations` reports no changes;
     `.venv/bin/ruff check` + `ruff format --check` on every touched file;
     `just migrate && just metric-setup` on the dev DB, where the registry build
     reports zero orphans for the migrated `StoreMetric` rows.
   - Done when all four hold and the observed output is captured.

## Completion Test

```bash
just python -m pytest django_spire/metric test_project/app/metrics --reuse-db -n 12 -q
just test
just make-migrations            # expect: No changes detected
.venv/bin/ruff check django_spire/metric test_project/app/metrics
.venv/bin/ruff format --check django_spire/metric test_project/app/metrics
just docs-tests
just migrate && just metric-setup
```

## Deviations

1. Object-separator constant renamed to `KEY_OBJECT_SEPARATOR`
   - What: Step 1 names the object-separator constant `KEY_OBJECT_SEPARATOR` instead of `OBJECT_SEPARATOR`.
   - Why: User redirect at approval — every key constant carries the `KEY_` prefix (`KEY_MAX_LENGTH`, `KEY_SEPARATOR`), so the object separator should too.
2. Word-separator constant renamed to `KEY_SEGMENT_SEPARATOR`
   - What: Step 1 names the within-segment (word) separator constant `KEY_SEGMENT_SEPARATOR` instead of `KEY_SEPARATOR`.
   - Why: User redirect at approval — "segment" makes clear the `-` joins words inside one local key segment, as opposed to `KEY_OBJECT_SEPARATOR`, the `--` that joins segments between nesting levels.
3. Word-separator constant renamed to `KEY_WORD_SEPARATOR`
   - What: Step 1 names the word separator constant `KEY_WORD_SEPARATOR` instead of `KEY_SEGMENT_SEPARATOR` (deviation 2).
   - Why: User redirect — `-` joins *words* (`order`, `revenue`); `--` is what splits *segments*/objects, so "segment separator" for `-` inverts the hierarchy. Final pair: `KEY_WORD_SEPARATOR = '-'`, `KEY_OBJECT_SEPARATOR = '--'`.
4. Fixed the four stale package-level `django_spire.metric` imports
   - What: Step 2 additionally updates `from django_spire.metric import Metric, ...` in `domain/management/commands/metric_build.py`, `test_metric_build.py`, `test_metric_remote.py`, and `test_metric_spec.py` to import from `django_spire.metric.metric` / `django_spire.metric.summary` / `django_spire.metric.utils`.
   - Why: False precondition discovered at step 1 — the user's in-flight emptied `django_spire/metric/__init__.py` makes the package-level re-exports ImportError, so the metric suite did not even collect at plan time. The fixes mirror what the user already did in `test_project/app/metrics/metrics.py`; without them no completion test is runnable.
5. Orphan badge class corrected to `text-bg-warning` in four metric templates
   - What: `orphan_badge.html`, `scroll/scroll.html`, `scroll/subdomain_scroll.html`, and `statistic/scroll/group_scroll.html` use `badge bg-warning`; changed to `badge text-bg-warning`.
   - Why: Discovered during step 6 verification — the two list-page orphan-badge tests (committed in `c88467d1`, failing on a clean HEAD worktree) assert `badge text-bg-warning`, and the orphan-badge backplan (`.backplan/2026-10-24-14-59-metric-registry-orphan-badge.md`, step 4) specifies `badge text-bg-warning`. The templates had deviated from their own approved plan; the change makes the committed tests pass without touching the tests.
6. Venv synced to the lock before step 6
   - What: `uv sync --all-extras --all-groups` (the `just venv` recipe also does `uv venv --clear` + `--upgrade`, which was heavier than needed).
   - Why: The venv was stale relative to `uv.lock` (django-glue 1.2.2 installed vs 1.3.0 locked); syncing also resolved the 19 pre-existing `core/components` Glue failures in the baseline full suite (4798 passed / 19 failed became 4844 passed / 0 failed).

# Fix 1.4.1 metric_build and changelog defects

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-10-28-11-47

## End State

`manage.py metric_build` builds every local registry and prints a skip line per
`REMOTE` registry without raising; `--registry` no longer flags rows declared by
other registries as orphaned; `docs/changelog/changelog.md` states the `MetricKey`
pattern correctly; `django_spire/constants.py` reads `__VERSION__ = '1.4.1'`;
and regression tests for both command bugs pass under
`just test-app django_spire/metric`.

## Observable Concern

The orphan pass must never count keys declared by a `REMOTE` registry as
"declared" — those describe rows on the other installation. Build mode must pass
only local registries to `_apply_orphans`, and when zero local registries are
built (an all-remote configuration) the orphan pass must be skipped entirely
rather than flagging every local row as orphaned.

## Current State

- `django_spire/metric/domain/management/commands/metric_build.py:34-58`:
  `handle()` passes the same `registries` list to the build loop (`:42-44`) and
  `_apply_orphans` (`:58`); with `--registry`, `_get_registries` returns only
  that one class (`:70-78`).
- `_apply_orphans` (`:80-118`) builds `declared` only from the registries it is
  given, then flags every active row whose key is not in that set — so
  `--registry X` orphans every other registry's rows.
- `Metric.build()` raises `ValueError` for `Target.REMOTE` registries
  (`django_spire/metric/metric.py:100-107`); `Metric.check()` handles remote via
  `_check_remote()` REST probes (`metric.py:111-116`). `metric_build` calls
  `build()` without checking `target`, so one remote registry tracebacks a plain
  run and stops later registries and the orphan pass.
- All seven `MetricKey` uses in `django_spire/metric/domain/statistic/api_v1.py`
  (`:24, 68, 88, 90, 107, 110, 127, 130`) take stored keys, which contain `--` by
  construction (`object_key`, `django_spire/metric/utils.py:17-26`).
  `STORAGE_KEY_PATTERN` (`django_spire/metric/key_utils.py:15`) rejects
  underscores and accepts `--`; local/spec keys separately reject `--` in
  `validate_local_key` (`key_utils.py:26-28`). The code is right.
- `docs/changelog/changelog.md:29-30` (v1.4.0 Breaking) says the `MetricKey`
  pattern "no longer accepts underscores or `--`" — the `--` half is wrong.
- Changelog v1.4.0 Added says the command "builds every registered registry"
  and that orphans are rows "declared in no registry"; `--registry`
  "builds one registry by its dotted path" — each true alone, inconsistent
  combined (the shipped behaviour).
- Tests live in `django_spire/metric/domain/tests/test_management.py`
  (`MetricBuildCommandTestCase`, `MetricBuildOrphanFlagTestCase`;
  `BaseTestCase` + `call_command` + `override_settings(DJANGO_SPIRE_METRIC_REGISTRY=...)`)
  and `test_metric_build.py` (Metric unit tests, incl.
  `test_remote_registry_cannot_build`).
- `get_object_from_module_string` (`django_spire/contrib/utils.py:61-69`) is
  import + getattr, so test-module classes are addressable by dotted path for
  `--registry` in regression tests.
- The test project registers `StoreMetric` and `TaskMetric`
  (`test_project/metric_settings.py:18-21`) — the paste's reproduction is valid.
- No v1.4.1 changelog section exists yet; by convention sections are dated at
  release (commit 02a21ac0), so the new section starts undated.
- Version: `django_spire/constants.py:1` holds `__VERSION__ = '1.4.0'`;
  `pyproject.toml:143` reads it dynamically (`version = { attr = ... }`), so the
  constant is the only version declaration. The v1.4.0 release commit (d8eae535)
  bumped only that constant (its pyproject.toml diff was a dependency bump).
  Latest tag is `v1.4.0`.
- Out of scope (user decision): housekeeping items — AGENTS.md "100 char lines"
  vs `ruff.toml` 120, and a Chores line for the intentional `.backplan/`
  un-ignoring (a650252c; user confirmed the un-ignore is intended).

## Plan

1. Skip the orphan pass with `--registry` (bug 1)
   - In `handle()`, call `_apply_orphans` only when `--registry` was not given
     (and not `--check`).
   - Done when `metric_build --registry X` leaves `is_orphaned` untouched for
     rows belonging to other registries.
2. Skip remote registries in build mode (bug 2)
   - In `handle()` build mode, partition registries by
     `target is Metric.Target.REMOTE`; build only the local ones and print one
     skip line per remote registry (label + "targets a remote installation").
   - Pass only local registries to `_apply_orphans`; when no local registry was
     built, skip the orphan pass entirely.
   - `--check` is unchanged — `check()` already probes remote targets.
   - Done when a plain `metric_build` with a registered remote registry exits
     cleanly, prints the skip line, builds the local registries, and does not
     count remote-declared keys as declared.
3. Correct the 1.4.0 MetricKey sentence (bug 3)
   - Reword `changelog.md:29-30`: the pattern "no longer accepts underscores (it
     accepts `--`, because the API takes the stored key form)".
   - Done when the sentence matches `STORAGE_KEY_PATTERN` behaviour.
4. Add the v1.4.1 changelog section
   - New undated `## v1.4.1` section at the top: `### Fixed` with the two
     `metric_build` fixes; `### Docs` noting the 1.4.0 MetricKey sentence
     correction.
   - Done when the section describes the shipped behaviour.
5. Nudge the project to v1.4.1
   - Set `__VERSION__ = '1.4.1'` in `django_spire/constants.py`. The changelog
     section stays undated; it is dated by the release commit, per convention.
   - Done when `django_spire.constants.__VERSION__` is `'1.4.1'`.
6. Add regression tests
   - In `django_spire/metric/domain/tests/test_management.py`, using
     test-module registry classes (dotted-path resolvable) plus
     `override_settings(DJANGO_SPIRE_METRIC_REGISTRY=...)`:
     - Two local registries registered; full build; then `--registry` for one;
       assert the other registry's rows are not flagged and its keys are not
       listed as orphans in the output.
     - One local + one remote registry; plain build; assert no exception, the
       skip line in output, and local rows built. Create a local row whose key
       is declared only by the remote registry and assert it IS flagged
       (remote keys are not "declared").
     - All-remote registry configuration; plain build exits cleanly and flags
       nothing.
   - Done when the new tests pass.
7. Lint and suite
   - `ruff check` + `ruff format` on changed files; `just test-app django_spire/metric`.
   - Done when both are clean.

## Completion Test

```
just test-app django_spire/metric   # full metric suite incl. new regression tests
ruff check django_spire/metric/ docs/changelog/
```

```
just python -c 'import django_spire.constants as c; print(c.__VERSION__)'   # 1.4.1
```

Secondary manual check (needs the test Postgres on 5439):

```
just python manage.py metric_build
just python manage.py metric_build --registry test_project.app.task.metrics.TaskMetric
```

The second run must list no StoreMetric rows as orphans and flag none. Then with
a temporary `REMOTE` registry in `DJANGO_SPIRE_METRIC_REGISTRY`, a plain
`metric_build` prints a skip line and exits 0.

## Deviations

1. Scope expanded to include the version bump.
   - What: added plan step 5 to set `django_spire/constants.py` `__VERSION__` to
     `1.4.1`, and updated the end state and completion test accordingly.
   - Why: user asked the plan to also nudge the project to v1.4.1.
2. Test Postgres was not running; the suite initially errored with connection
   refused on port 5439.
   - What: started the CI test container
     (`docker compose -f test_project/docker-compose.test.yml up -d`) before
     running the suite; no plan step changed.
   - Why: the completion test requires the test database the suite expects.
3. The dev database `localhost-django-spire` on port 5432 does not exist, so the
   secondary manual check could not run against the dev DB.
   - What: ran the identical manual reproduction against a scratch database
     (`django_spire_manual`) created on the 5439 test Postgres container, with
     the same `DATABASE_*` overrides the settings module reads.
   - Why: the local dev DB was never provisioned in this environment; the
     scratch DB exercises the same command path against the same registered
     registries (StoreMetric, TaskMetric).

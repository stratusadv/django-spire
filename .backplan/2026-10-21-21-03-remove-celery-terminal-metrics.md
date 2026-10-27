# Remove Celery terminal-metric tracking

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-21-21-03

## End State

The celery app fires no terminal metric events anywhere: `celery/metrics.py` is deleted,
`record_terminal_metric` / `TERMINAL_METRIC_REFERENCES` and the four `celery_task_*`
references appear nowhere in `django_spire/` or `test_project/`, the celery suite and full
suite pass, and AGENTS.md + changelog state that task outcomes are derived from the
`CeleryTask` rows themselves. Nothing is committed.

## Observable Concern

`CeleryTaskService._apply_backend_snapshot` currently returns a bool (`records_metric`)
whose only purpose is the metric gate; `update_from_backend` and three
`ApplyBackendSnapshotTestCase` tests consume that return value. The most likely mistake is
leaving a dangling `if self._apply_backend_snapshot(...)` gate or an unused
`records_metric` variable behind, which ruff (ARG/F rules) and the tests will catch.

## Current State (verified)

Production code:

- `celery/metrics.py` - `TERMINAL_METRIC_REFERENCES` (SUCCESS/FAILURE/RETRY/REVOKED ->
  `celery_task_success/failure/retry/canceled`) + `record_terminal_metric(state)`; added by
  the fix plan, step 3.
- `celery/services/service.py` - import at :15; `record_terminal_metric(new_state)` at :200
  (gated on `_apply_backend_snapshot`'s bool return); `record_terminal_metric(states.REVOKED)`
  at :226 in `cancel()`; `records_metric = state in TERMINAL_METRIC_REFERENCES and ...` at
  :260-262 returned at :287 (also `return False` early exits at :258/:283); docstring
  :242-244 describes the metric return contract.
- `celery/manager.py` - import at :23; `record_terminal_metric(states.FAILURE)` at :198 in
  `_create_failed_celery_task`.
- `celery/management/commands/prune_stale_started_celery_tasks.py` - import at :12;
  `for _ in range(stamped): record_terminal_metric(states.FAILURE)` at :120-122.

Tests (all patch
`django_spire.metric.domain.statistic.services.tracking_service.StatisticTrackingService.track_configured`
or the per-module `record_terminal_metric`):

- `tests/test_metrics.py` - entire file (delete).
- `tests/test_commands.py` - `test_failure_stamp_records_terminal_metric` (:215-230, delete);
  `test_no_live_workers_skips_failure_stamp` (:232-248, drop the metric patch/param/assert,
  keep the ping-guard assertions).
- `tests/test_managers/test_base_celery_task_manager.py` - `test_send_failure_records_terminal_metric`
  and `test_dedupe_reuse_records_no_metric` (delete both; the top-level
  `KombuOperationalError` import is still used by ~10 other tests).
- `tests/test_services/test_celery_task_service.py` - `_TRACK_CONFIGURED` constant (:16-19);
  20 `@patch(_TRACK_CONFIGURED)` decorators (:101-:658, :773) each adding a
  `mock_track_configured` parameter; 17 `assert_called_once_with(reference=...)` asserts,
  2 `assert_not_called()` asserts; `test_cancel_fires_canceled_metric_once` (:773-781,
  delete whole test); `ApplyBackendSnapshotTestCase` (:674-728): 3 tests consume the
  `records_metric` bool return (drop the assignment + assert, keep the behavior asserts).
- `tests/test_views.py` - `_TRACK_CONFIGURED` (:26-28), one patch/param (:272-274), one
  assert (:313).
- `tests/test_services/test_resolver.py` - `_TRACK_CONFIGURED` (:16-18), patch/param
  (:67-69), `references` collection + `sorted(references) == [...]` assert (:86-87).
- `tests/test_async_result_integration.py` - patch/param (:77-81), one assert (:93).
- `tests/test_race_harness.py` (untracked session-2 artifact) - `_track_configured`
  collector (:196), patch with side_effect (:217-218), `assert metric_calls ==
  ['celery_task_success']` (:238) - drop the collector/patch/assert, keep the race asserts.

Docs:

- `AGENTS.md` :416 (four terminal references + `celery/metrics.py` helper sentence), :464
  (reaper: "real terminal + exactly-once metric" + the per-stamped-row metric sentence),
  :483 (Key files: `celery/metrics.py` entry).
- `docs/changelog/changelog.md` v1.3.1 Fixes bullet "Terminal metrics now fire exactly once
  on every terminal transition..." - becomes a Changes bullet documenting the removal.
  (v1.3.0 entry is historical and stays as written.)

## Plan

1. **Strip production emissions**
   - Delete `celery/metrics.py`.
   - `service.py`: drop the import; `update_from_backend` calls `_apply_backend_snapshot`
     unconditionally (no gate); drop the `cancel()` emission; `_apply_backend_snapshot`
     loses `records_metric` and returns nothing (early exits become bare `return`s),
     docstring updated.
   - `manager.py`: drop import + failure emission.
   - Reaper: drop import + per-stamped-row loop (keep the `stamped` count + output line).
   - Done when `grep -r 'record_terminal_metric|TERMINAL_METRIC_REFERENCES' django_spire/`
     returns nothing.
2. **Strip metric tests** (per the Current State list: delete 2 test files' content /
   2 whole tests / 20+ patch-decorator-param-triples, keep every non-metric assertion)
   - Done when `grep -r 'track_configured|_TRACK_CONFIGURED|metric' django_spire/celery/tests/`
     returns nothing.
3. **Docs**
   - AGENTS.md :416 -> state machine sentence without metrics, plus one clause that
     terminal outcomes are not fired as separate metric events (derivable from the
     `CeleryTask` rows); :464 reaper paragraph without metric mentions; :483 Key files
     drops `celery/metrics.py`.
   - Changelog v1.3.1: replace the metrics Fixes bullet with a `### Changes` bullet:
     terminal metric tracking removed, outcomes derivable from `CeleryTask` rows.
   - Done when no `celery_task_*` reference remains outside `docs/`.
4. **Verify**
   - `just python -m pytest django_spire/celery/tests/ --reuse-db -q` -> all passed.
   - `just test` -> all passed.
   - Lint histogram diff vs HEAD baseline (celery tree) empty; `ruff format --check` clean.
   - Done when all four hold; quote real output into this doc.

## Completion Test

1. `just python -m pytest django_spire/celery/tests/ --reuse-db -q` -> all passed.

   ```
   ============================== 435 passed in 9.85s ==============================
   ```

2. `just test` -> all passed.

   ```
   ============= 4607 passed, 2 warnings, 4 subtests passed in 45.81s =============
   ```

   Same two pre-existing warnings as before the change.

3. `grep -rn 'record_terminal_metric|TERMINAL_METRIC_REFERENCES|celery_task_success|celery_task_failure|celery_task_retry|celery_task_canceled' django_spire/ test_project/` -> no matches (`grep_exit=1`). Two stale `__pycache__/*.pyc` files of the deleted modules matched initially and were removed.

4. `diff /tmp/baseline_norm.txt /tmp/current_norm.txt` -> empty (`LINT_DIFF_CLEAN`); `ruff format --check django_spire/celery/` -> `54 files already formatted`.

5. `git status --short` + `git log --oneline -1` -> intended changes only (plus the user's uncommitted pyproject.toml/uv.lock and the untracked session-2 `test_race_harness.py`); `a2dfb58d indent typo` (HEAD unchanged, nothing committed).

## Deviations

1. Two fix-plan artifacts reverted byte-for-byte to HEAD.
   - What: `celery/manager.py` and `tests/test_managers/test_base_celery_task_manager.py` no longer show in `git status`.
   - Why: the removal undid exactly what the fix plan had added to those two files (the send-failure emission + `failed_task` assignment, and the two metric tests + top-level kombu import), leaving them identical to HEAD. Deleting the intermediate `record_terminal_metric` call also unmasked a latent `RET504` on the `failed_task` assignment, which the direct `return CeleryTask.objects.create(...)` form fixes.

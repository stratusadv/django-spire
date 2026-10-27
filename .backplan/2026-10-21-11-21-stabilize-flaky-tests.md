# Stabilize the two flaky tests — 2026-10-21-11-21

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed

## End state

Both previously flaky tests — `django_spire/celery/tests/test_scheduler.py::TestSchedulerThread::test_scheduler_loop_sends_due_slot_once` and `django_spire/contrib/admin/tests/test_admin_smoke.py::AdminSmokeTests::test_every_change_form_loads` — pass across repeated runs, and the CeleryTask admin change form no longer 500s for a FAILURE task whose result payload is empty or corrupt.

## Completion test

```bash
# 1. Full suite, 3 consecutive green runs (the original flake context):
just test
just test
just test

# 2. Targeted loops on the two flaky files:
just python -m pytest django_spire/contrib/admin/tests/test_admin_smoke.py --reuse-db -q   # 6 consecutive green
just python -m pytest django_spire/celery/tests/test_scheduler.py --reuse-db -q            # 3 consecutive green

# 3. New regression test for the production bug:
just python -m pytest django_spire/celery/tests/test_admin.py --reuse-db -q -n 0
```

## Current state

Verified facts (all re-checked in this session; nothing from memory):

- Branch `nathanj/celery-update`, HEAD `61ebc7c4` ("Migrate robit cron jobs to the embedded Celery scheduler"). Working tree carries the prior session's legitimate uncommitted work (sweep/resolver/crash-logging/settings move) — untouched by this plan.
- Full-suite run last session: **2 failed, 4547 passed** — the two flaky tests named above.

### Flake 1: `test_scheduler_loop_sends_due_slot_once` — root cause: test-transaction bug (production code is sound)

- `TestSchedulerThread` carries a class-level non-transaction `@pytest.mark.django_db`. The test under test spawns the real scheduler **loop thread**, which does DB work (`get_or_create`/`update` on `CelerySchedulerTask`) on its own autocommit connection.
- The test's opening `CelerySchedulerTask.objects.filter(schedule_key=_LOOP_ROW_KEY).delete()` runs inside the test's rolled-back transaction and is **invisible** to the loop thread (PostgreSQL isolation). Under `--reuse-db`, loop-thread writes from earlier runs are autocommitted and persist, so the next run's loop thread `get_or_create` returns the **stale committed row** the test believed it had deleted.
- DIAG evidence captured on every failing run: `skip(last_sent>=moment) moment=2026-01-01 23:59:30 last_sent=2026-01-02 00:59:30` — the row already carried the stale value, so `claim_schedule_slot` correctly skipped and the expected send never happened.
- A main-thread tight-loop diagnostic proved the production logic deterministic and correct: exactly one send at tick 2, then `last_sent >= moment` skips. `claim_schedule_slot` is sound.
- Project's established pattern for thread-DB tests is `@pytest.mark.django_db(transaction=True)` — already used by `test_concurrent_claimers_produce_single_send` (same file) and `TestSweepLoop` (test_sweep.py); AGENTS.md documents the gotcha.
- **Candidate fix already applied and validated in the worktree**: `@pytest.mark.django_db(transaction=True)` on the single test method. Evidence: 6/6 serial runs green (was 6/6 failing at HEAD), first-claim DIAG line shows fresh-row semantics, 3/3 full-file xdist runs green, `test_sweep.py` 11 passed, lint/format clean.

### Flake 2: `test_every_change_form_loads` — root cause: production robustness bug, exposed by a hash-order lottery

- Failure mode: 500 on the CeleryTask admin change form. Final exception chain (captured): `admin/helpers.py:278 → lookup_field → getattr(obj, 'exception_result') → models.py:110 → has_exception_result → models.py:106 → pickle.loads(b'') → EOFError: Ran out of input`.
- **Production bug**: `CeleryTask.has_exception_result` (models.py:102-106) calls `pickle.loads(self._result)` with **no guard** when `state == FAILURE`. The sibling `has_result` (models.py:86-95) already guards the identical unpickle (`if not self._result` + `except (EOFError, pickle.UnpicklingError)`). Any FAILURE row with an empty/corrupt `_result` 500s the admin change form and any template using the property (e.g. `task_content.html:143`).
  - The normal web-writer path (`_apply_terminal_snapshot`) always pickles a `CeleryExceptionResult` on FAILURE, so this is a **data-shape anomaly** path (manual DB edit, truncation, future write path) — but display code must survive any row shape, and the sibling property sets that precedent.
- **Why flaky**: the generic admin smoke factory (`factories.py::_scalar_value`) seeds choice fields with the **first** choice. `CeleryTask.state` choices come from `_celery_state_choices()`, which iterates `celery.states.ALL_STATES` — a **frozenset** in Celery (verified in venv source). Iteration order is hash-randomized per process (verified: 5 consecutive interpreter runs produced 5 different orders). So ~1/7 of xdist worker processes seed `state='FAILURE'`; combined with the factory's BinaryField default `_result=b''`, the unguarded unpickle fires.
- DIAG capture from a failing run: `DIAG-SMOKE: pk=636 state='FAILURE' _result=b'' task_id=00000000-...-00000000001d` — the factory-built instance itself was FAILURE with empty result. Flake rate observed: ~1 failing run in 3-6 file runs.
- **Deterministic repro (no lottery)**: a FAILURE CeleryTask with `_result=b''` + GET its change form → 500, 100% reproducible (scratch test, currently `django_spire/celery/tests/test_zz_diag.py`).
- The `RemovedInDjango70Warning` (ADMINS `(name, address)` pairs) seen in the failure output is a **red herring**: it comes from Django's error-email machinery reacting to the 500. The deprecated ADMINS format in `test_project/base_settings.py:29` is a separate one-line hygiene issue (optional step 6 below).
- Existing celery admin tests (`test_admin.py`) never hit the bug because `create_test_celery_task` always stores a *valid* pickle (default `pickle.dumps(CeleryNoResult())`), even for `state=FAILURE`.
- **Candidate fix 1 already applied and validated in the worktree**: `has_exception_result` guarded to mirror `has_result`. Evidence: deterministic repro now 200; all 378 celery tests pass; admin smoke file 3/3 green (was ~1 in 3 failing); lint/format clean (one pre-existing DJ001 at HEAD on `model_key`, untouched).
- Secondary observations (not acted on, recorded for honesty):
  - `_apply_terminal_snapshot` (service.py:309-316) handles `exception_result is None` for the message but dereferences `exception_result.traceback` unguarded — latent, no caller currently passes `None` on FAILURE.
  - `CeleryTaskStateFilter.lookups` (admin.py:24) also iterated the frozenset, so the admin state-filter dropdown order was per-process non-deterministic (cosmetic) — addressed by plan step 3.
  - `stop_scheduler` clears the stop event even if `join` times out (thread would keep running with a cleared event). Latent, unrelated to these flakes.
  - `test_start_is_idempotent` / `test_stop_clears_thread` spawn the loop thread without `transaction=True`, but their assertions never depend on loop-thread row visibility (stable so far).

## Plan

1. Keep the validated `transaction=True` on `test_scheduler_loop_sends_due_slot_once`
   - Already applied in the worktree; the project's established pattern for thread-DB tests. No further change.
   - done when the step-5 scheduler file loop is green.
2. Keep the validated `has_exception_result` guard and add the permanent regression test
   - Guard already applied in models.py (mirrors `has_result`). Move the validated scratch repro out of `django_spire/celery/tests/test_zz_diag.py` into `CeleryTaskAdminTestCase` (test_admin.py) as `test_change_form_loads_for_failure_task_with_empty_result`, built via the existing `create_test_celery_task(state=states.FAILURE, _result=b'')` helper; assert change form 200 and `exception_result is None`. Delete `test_zz_diag.py`.
   - done when `test_admin.py` passes, `test_zz_diag.py` is gone, and the new test fails if the guard is reverted.
3. Make `CeleryTask.state` choices deterministic (removes the lottery that made the bug probabilistic)
   - models.py: add a module-level `_CELERY_STATE_ORDER` tuple (PENDING, RECEIVED, STARTED, RETRY, FAILURE, SUCCESS, REVOKED — lifecycle order, PENDING first to match the field default) and have `_celery_state_choices()` iterate it instead of the `states.ALL_STATES` frozenset.
   - admin.py: `CeleryTaskStateFilter.lookups` uses the same tuple instead of `list(states.ALL_STATES)` (also fixes the cosmetic dropdown non-determinism).
   - Field deconstruction references the function, so no schema change — verify with `just python manage.py makemigrations --check --dry-run` (must report no changes).
   - done when the order is stable across interpreter processes, no new migration is detected, and celery + admin test files pass.
4. Lint and format the touched files
   - `ruff check` + `ruff format --check` on models.py, admin.py, test_admin.py, test_scheduler.py.
   - done when both pass (pre-existing HEAD errors excluded).
5. Run the completion test
   - 3 consecutive `just test` full-suite runs, the 6x admin-smoke loop, the 3x scheduler-file loop, and `test_admin.py` serial. Capture the real output.
   - done when all runs are green; any new unrelated failure is reported, not chased.
6. (Optional — user call) Fix the deprecated ADMINS format
   - `test_project/base_settings.py:29`: `ADMINS = [('Stratus', 'stratus@stratusadv.com')]` → `ADMINS = ['stratus@stratusadv.com']` per Django 6.0's deprecation message. Removes the warning from every future error email; independent of both flakes.
   - done when the setting parses and the celery + admin test files still pass.

Riskiest step: step 5 — three full-suite runs are where any *other* latent flake would surface; the plan is to stop and report rather than expand scope.

## Deviations

none

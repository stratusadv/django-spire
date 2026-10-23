# Task resolver (background sync) — 2026-10-19-11-41

Status: Executed

## End state

Stored `CeleryTask` state that is non-terminal is re-synced from the result
backend by (a) a multi-instance-safe background sweep that runs in the web
process, (b) an on-demand resolve when the unready list views (item/toast)
render, and (c) an opt-in gate in `BaseCeleryTaskManager.send_task` that
resolves the manager's unready tasks before deciding to send a new one or
reuse — so a task that finished while nobody was polling its widget shows as
completed on the next page load, and the scheduler (or any send) for an
opted-in manager never double-starts work that is still running, and does
start new work when the previous run actually finished.

## Completion test

```bash
just python -m pytest django_spire/celery/tests/ --reuse-db -q
# includes the new tests:
#   resolver: bulk resolve to backend terminal (state + pickled result + metric once),
#             stored-terminal rows untouched, limit respected, per-task exception isolation
#   list view: task finished in backend but stored STARTED is no longer rendered unready
#   gate: stale STARTED with backend SUCCESS sends; backend still STARTED reuses; non-opt-in unchanged
#   sweep: lifecycle (disabled/enabled/double-start/stop) + claim race (exactly one winner) + winner resolves
just test
.venv/bin/ruff check django_spire/ test_project/
.venv/bin/ruff format --check django_spire/ test_project/
just python manage.py makemigrations --check --dry-run
```

## Current state

Verified facts (step 0, re-read this session):

- Root cause of both use cases: the only things that refresh a stored
  `CeleryTask` are the single-task widget poll, the reaper command, or a
  view that calls `update_from_backend`:
  - `_task_view` (`django_spire/celery/views/task_views.py:20-27`) DOES call
    `celery_task.services.update_from_backend()` (line 23).
  - `_list_view` (`task_views.py:57-73`) does NOT — it renders stored
    `by_unready()` state, so a task that finished while nobody viewed its
    item/toast stays "running" until someone opens that task page.
- The per-task engine is proven and must be reused, not reinvented:
  `CeleryTaskService.update_from_backend()`
  (`django_spire/celery/services/service.py:173`) = backend meta read +
  `_apply_backend_snapshot` (line 237: `transaction.atomic` +
  `select_for_update` + `CeleryTaskStateMachine.ok` guard +
  `_row_has_changed` skip + `_save_snapshot`); the terminal metric fires
  exactly once per transition via the boolean return (line 204-207).
- State machine (`django_spire/celery/state_machine.py:38-52`): terminals
  sticky, PENDING/RECEIVED unreachable after leaving, custom states anchor
  to STARTED. Stored terminal rows are safe to skip.
- Backend reads are per-task only (`async_result._get_task_meta()`,
  `get_task_meta(derive_final_meta_key(...))`); there is no public batch API.
  Bulk resolve = one select of non-terminal rows + N backend reads + N small
  apply transactions.
- `by_unready()` (`django_spire/celery/querysets.py:27-28`) =
  `exclude(state__in=[*READY_STATES, *EXCEPTION_STATES])` → PENDING /
  RECEIVED / STARTED / RETRY + custom progress states.
- `dedupe_unready` (`django_spire/celery/manager.py:45`, checked 123-126)
  reuses the first stored-unready task and never checks the backend: a task
  that actually finished still blocks a new send with a stale row.
- The multi-instance atomic claim is reusable as-is:
  `claim_schedule_slot` (`django_spire/celery/scheduler.py:117-147`) wins by
  rowcount on one atomic UPDATE —
  `filter(schedule_key=..., last_sent_datetime__lt=target_slot).update(last_sent_datetime=moment, claimed_by=...)`
  (lines 140-142) — portable to Postgres and SQLite.
- The daemon-thread pattern to mirror (`scheduler.py`): `_SchedulerState`
  (thread/stop_event/start_lock, line 24), `_instance_id()` (150),
  `_scheduler_loop` (164: per-entry try/except, `stop_event.wait`,
  `close_old_connections()` in finally), `start_scheduler` (198: gated on
  settings + `RUN_MAIN` + alive check under the start lock),
  `stop_scheduler` (227). Started from `CeleryConfig.ready()`
  (`django_spire/celery/apps.py:31-33`).
- Claim-row model template: `CelerySchedulerTask`
  (`django_spire/celery/models.py:256-271`: unique `schedule_key`,
  `last_sent_datetime`, `claimed_by`).
- Settings pattern: framework defaults in `django_spire/settings.py:23-25`
  (`DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES/ENABLED/TICK_SECONDS`), project
  opt-in `test_project/base_settings.py:229-232` (ENABLED=True), tests
  `test_project/test_settings.py:24` (ENABLED=False).
- The scheduler sends through `manager_class().send_task(**kwargs)`
  (`scheduler.py:147`), so a gate inside `send_task` covers scheduled sends
  with zero scheduler changes.
- Test layout: `django_spire/celery/tests/` (thread-lifecycle pattern in
  `test_scheduler.py`; services in `test_services/`, managers in
  `test_managers/`). Gotchas from prior work: non-main-thread DB access
  needs `@pytest.mark.django_db(transaction=True)`; xdist workers share one
  test DB, so rows threads race on need test-unique keys.
- House style: ruff `select=["ALL"]`, single quotes, 100 cols, no code
  comments (AGENTS.md); migrations excluded from ruff.

Assumptions (flagged per skill step 1; adjust at review):

- Naming follows neighbors: `resolve_celery_tasks`,
  `resolve_unready_before_send`, `CeleryTaskSweep`, `sweep.py`,
  `DJANGO_SPIRE_CELERY_SWEEP_*`.
- Sweep defaults: interval 30 s, per-sweep cap 100 tasks (FIFO by
  `queued_datetime`; the rest are picked up next window), one sweep key
  `'default'` (the key field exists so tests can use unique rows and
  projects can add more sweeps later).
- The sweep is a separate daemon thread from the scheduler — resolution
  works whether or not `DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED` is set — and
  is independently gated by `DJANGO_SPIRE_CELERY_SWEEP_ENABLED`
  (framework default False; test project True; tests False).
- The resolver returns the count of rows whose stored state changed
  (callers only need progress, not a mapping).
- v1 does no backend batch read (no public API for it); a direct
  `WHERE task_id IN (...)` read of the PG backend table is a possible later
  optimization, not now.

## Plan

1. Resolver core (steps 2, 3, 4 all hang on this)
   - New `django_spire/celery/services/resolver.py` with
     `resolve_celery_tasks(celery_tasks: QuerySet[CeleryTask], *, limit: int | None = None) -> int`:
     iterate the queryset in queued order, call each task's existing
     `task.services.update_from_backend()`, wrap each task in
     try/except (log + continue), return the count of rows whose stored
     state changed (compare `state` before/after; `_save_snapshot` only
     touches `self.obj` when the row actually changed).
   - Reuses the whole proven engine: no new backend reads, state-machine
     guards, monotonic-progress, or metric logic.
   - done when `test_services/test_resolver.py` passes: a STARTED row whose
     backend is terminal resolves (state + pickled result/exception +
     terminal metric exactly once); a stored-terminal row is left untouched;
     `limit` is respected; one task's backend exception does not stop the
     remaining tasks.
2. On-demand list resolve (depends on 1; parallel with 3 and 4)
   - `task_views.py:_list_view`: when `show_all` is not set, call
     `resolve_celery_tasks(celery_tasks.by_unready())` before rendering,
     then re-apply `by_unready()` so the response lists only tasks still
     unready after the fresh resolve.
   - done when a list-view test shows a task whose backend reached SUCCESS
     but whose stored row is STARTED no longer renders unready, and the row
     is terminal in the DB afterwards.
3. Opt-in start-new gate (depends on 1; parallel with 2 and 4)
   - `manager.py`: new class attribute
     `resolve_unready_before_send: bool = False`. In `send_task`, when set,
     first `resolve_celery_tasks(self.filter_celery_tasks().by_unready())`,
     then run the existing dedupe check (shared with `dedupe_unready`)
     against the fresh stored state: still unready → return the existing
     task (no send); actually finished → proceed to send.
   - `dedupe_unready` alone keeps today's behavior exactly (Q2: opt-in).
   - Because the scheduler sends via `send_task`, opted-in cron entries get
     the gate with no scheduler change.
   - If the backend is unreachable during the gate, the resolve changes
     nothing and the dedupe check degrades to today's stored-state
     `dedupe_unready` behavior.
   - done when `test_managers/` tests pass: (a) stale STARTED row with
     backend SUCCESS → a new task is sent, (b) backend still STARTED → the
     existing task is returned and no new send happens, (c) a
     non-opt-in manager is byte-for-byte today's behavior.
4. Background sweep (depends on 1; parallel with 2 and 3; riskiest)
   - Model `CeleryTaskSweep` in `models.py` mirroring `CelerySchedulerTask`:
     unique `key` (default `'default'`), `last_swept_datetime`,
     `claimed_by` + migration.
   - New `django_spire/celery/sweep.py` mirroring `scheduler.py`:
     `_SweepState`; `claim_sweep_window(key, interval_seconds, claimed_by)`
     (get_or_create the row seeded with `last_swept_datetime=moment`, then
     one atomic
     `filter(key=..., last_swept_datetime__lt=moment-interval).update(last_swept_datetime=moment, claimed_by=...)`,
     rowcount == 1 wins — same exactly-once semantics as the scheduler,
     including fresh rows first claiming on the next window, never
     retroactively; a crash mid-sweep consumes the claim, so the rest of the
     batch is picked up on the next window — no replay, no duplication); `_sweep_loop` (wait on stop event → claim →
     `resolve_celery_tasks(CeleryTask.objects.by_unready(), limit=...)`,
     per-window try/except so one bad window never kills the loop,
     `close_old_connections()` each iteration + finally); `start_sweep()` /
     `stop_sweep()` with the same gating as `start_scheduler`
     (setting + `RUN_MAIN` + alive check).
   - `apps.py:ready()` calls `start_sweep()` after `start_scheduler()`.
   - Settings: `django_spire/settings.py` —
     `DJANGO_SPIRE_CELERY_SWEEP_ENABLED = False`,
     `DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS = 30`,
     `DJANGO_SPIRE_CELERY_SWEEP_TASK_LIMIT = 100`;
     `test_project/base_settings.py` — ENABLED True;
     `test_project/test_settings.py` — ENABLED False.
   - done when `test_sweep.py` passes: disabled → `start_sweep()` is False;
     enabled → thread starts, double-start False, stop joins; two racing
     claimants on one row → exactly one True; a winning claim resolves a
     seeded unready task (transaction=True, test-unique sweep key per test
     for xdist); `makemigrations --check --dry-run` clean.
5. Docs (depends on 1-4)
   - AGENTS.md Celery section: one short paragraph — one engine
     (`update_from_backend`), three triggers (background sweep, on-demand
     list resolve, opt-in send gate), the new settings, the
     `CeleryTaskSweep` claim row, and that the gate covers scheduler sends.
   - done when the doc matches the implemented names and behavior.
6. Verify (depends on all)
   - Run the completion test commands and capture real output.
   - done when every command is green.

## Failure modes

The resolver holds no state, so "interrupted" means "the loop stopped
partway"; every apply is one atomic, re-entrant, per-row transaction.

- Per-task failure (backend read error, DB error): caught and logged by the
  resolver, the loop continues; `update_from_backend` already retries
  transient backend errors on the next poll (`_RESULT_UNAVAILABLE`).
- Row-level atomicity: each apply is its own `transaction.atomic` — a crash
  mid-apply rolls back that row only; no partial rows, no cross-row
  transaction exists to roll back.
- Sweep window lost (crash/restart mid-batch): the claim is consumed before
  the work, so the remainder of the batch waits for the next window (≤ one
  interval of extra staleness, bounded by the cap); no replay, no duplicate
  backend reads.
- Multi-instance: the atomic claim gives one winner per window (losers never
  read the backend); even if two appliers raced the same row,
  `select_for_update` + the sticky-terminal state machine drops the second
  transition, so the terminal metric stays exactly-once (defense in depth).
- Graceful web shutdown: daemon thread dies with the process; Postgres rolls
  back open transactions; the claim stays consumed, so no double sweep after
  restart.
- Worker down: the backend still reports unready (true — the task is queued)
  → the gate keeps deduping correctly.
- Stuck STARTED with no terminal write (worker died mid-task): NOT
  resolvable by the sweep — there is no terminal in the backend to read;
  that remains `prune_stale_started_celery_tasks`' job. The sweep
  complements the reaper, it does not replace it.
- All web instances down: nothing resolves (the web is the single writer);
  inherent to the architecture; the reaper remains the manual backstop.
- Known tiny edge (pre-existing, shared with the single-task poll): a crash
  between the apply commit and the terminal-metric record loses that one
  metric; the row state is still correct.

## Deviations

1. Completion test ruff criterion adjusted
    - The plan required `ruff check` / `ruff format --check` green across all
      of `django_spire/` + `test_project/`, but the HEAD tree already carried
      59 pre-existing lint errors and one pre-existing format-drift file
      (verified against `git show HEAD:` baselines), so a tree-green lint was
      not reachable as a precondition.
    - The re-derived criterion — zero NEW violations on touched files
      (verified by diffing the HEAD baseline), the full test suite green, and
      `makemigrations --check` clean — was met: the touched files report only
      pre-existing findings on lines not written by this change.
2. Dev-DB migration apply not run
    - `just python manage.py migrate django_spire_celery` failed because
      `development.env` points at a local database
      (`localhost-django-spire`, port 5432) that does not exist on this
      machine (only `stratus` / `stratusadv-portal` do).
    - The `0012_celerytasksweep` migration is verified by the pytest run
      (the test DB on 5439 migrates from scratch, full suite green);
      applying it to the real dev DB is left as a manual step once that DB
      is available.

# Embedded celery worker with multi-instance-safe cron — 2026-10-16-23-02

Status: Executed

## Goal (confirmed)

A `CeleryScheduler` class in `django_spire.celery.scheduler` used seeder-style: a
project subclasses it and declares a `tasks` list of cron schedule entries. A daemon thread
started with the Django web process sends the referenced celery tasks to the broker
when each cron slot is due, so multiple web instances never double-fire a slot.

Decisions confirmed with the user:
- Startup: auto daemon thread on Django startup, gated by a setting.
- Execution: beat-style, send to the broker (existing celery worker pool executes).
- Guard: per-schedule-slot atomic DB claim (works on Postgres and SQLite, no new deps).

## End state

`just run-server` with the worker enabled sends at most one copy of each cron task
per slot even with several web instances running; scheduled runs appear as normal
`CeleryTask` records in the celery UI/admin; `just test` is green including a
concurrent-claim test that proves exactly-once.

## Completion test

```bash
just test-app django_spire/celery      # new worker tests green
just test                              # full suite green
ruff check <touched files>             # zero NEW issues (repo baseline has ~1060 pre-existing errors)
ruff format --check <touched files>    # clean
```

Manual smoke (optional): with `DJANGO_SPIRE_CELERY_WORKER_ENABLED` true and a
`*/1`-minute entry, two `runserver` processes produce exactly one new `CeleryTask`
row per minute.

## Current state (verified)

- `django_spire/celery/` app: label `django_spire_celery`; `CeleryConfig.ready()`
  only calls `check_required_apps`; migrations through 0009; `CeleryTask` is a plain
  model with `CeleryTaskQuerySet` + `CeleryTaskService`; `CeleryTaskAdmin` exists.
- `BaseCeleryTaskManager.send_task()` (manager.py:120) is the existing send path:
  kwargs validation, exponential-backoff retries, `spire_*` headers, creates the
  `CeleryTask` record, and on send failure creates a FAILURE record with
  `SendFailedError`. It publishes via `celery.execute.send_task`, a proxy that
  resolves to the current celery app at call time.
- The web process already registers the project celery app
  (`test_project/__init__.py:4`), so sending from a web-process thread uses the
  configured broker (`CELERY_BROKER_URL`).
- `celery==5.6.3` (hard dep) provides `celery.schedules.crontab.from_string()`
  (standard 5-field cron, robit-compatible) with `is_due(last_run_at)` and
  `remaining_estimate(last_run_at)`; verified: `is_due` is true when the next slot
  after `last_run_at` has passed. No `freezegun` in dev deps, so tests need an
  injectable `nowfun` (celery crontab already supports one).
- Seeder pattern to mirror (`contrib/seeding/seeder.py`): declarative class
  attributes, `__init_subclass__` validation raising `ValueError`, helper
  constructors, `name_verbose`.
- Settings precedent: `DJANGO_SPIRE_SEARCH_REGISTRY` / `DJANGO_SPIRE_REPORT_REGISTRIES`
  in `django_spire/settings.py`, read through the `django_spire/conf.py` wrapper.
- Thread precedent: tracker flusher thread and metric queue worker (daemon, named).
- Today's cron-with-Django is robit: `test_project/worker.py` runs a separate
  robit process with `cron='0 0 * * 6'` jobs calling Django services inline — the
  exact duplicate-fire problem when two instances deploy. Migrating those jobs is
  out of scope; this plan replaces the pattern going forward.
- Settings chain: `test_settings → postgres_settings → base_settings` (star
  imports), so a default-False setting flipped on in `base_settings` must be
  explicitly turned off in `test_settings` (same pattern as the metric click
  tracking guard there).
- No existing schedule/cron machinery in `django_spire` (grep for crontab/CRON
  returns nothing in the framework).

## Exactly-once mechanism (the core design)

One DB row per schedule entry (`CeleryWorkerSchedule`), field
`last_sent_datetime` = the wall time of the last successful claim (beat semantics,
so a worker that was down never replays missed slots — it fires at most once and
reschedules from now).

Per tick, per entry (all instances read the same shared row):

1. `due = crontab.is_due(last_sent_datetime)` — true iff a slot passed since the
   last claim.
2. If due: `target = now + crontab.remaining_estimate(last_sent_datetime)` — the
   exact slot time; a pure function of the shared `last_sent_datetime`, identical
   on every instance regardless of local clock.
3. Atomic claim:
   `filter(schedule_key=k, last_sent_datetime__lt=target).update(last_sent_datetime=now, claimed_by=instance)`
   — a single atomic UPDATE; row locks serialize racing instances; only the first
   sees `rowcount == 1` and sends. A racer re-evaluates the WHERE against the
   winner's new value (>= target) and gets 0 rows.
4. Winner calls `entry.manager().send_task(**entry.kwargs)` (full existing send
   path: record + headers + retries + send-failure record).

Clock skew can only delay a fire, never duplicate one: an instance's due check
guarantees `target <= its own now` before it claims, so the value it writes is
always `>= target`. Row created at startup with `last_sent_datetime = now`, so the
first fire is the next future slot (never retroactive). Portable: plain
`filter().update()` works on Postgres and SQLite.

## Plan

1. Settings + declarative scheduler classes
   - `django_spire/settings.py`: `DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES = []`,
     `DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED = False`,
     `DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS = 30`.
   - New module `django_spire/celery/scheduler.py`:
     `SchedulerTask(manager, crontab, *, name=None, kwargs=None)` — validates the
     crontab string up front via `crontab.from_string`; and `CeleryScheduler`
     with required `tasks: list[SchedulerTask]` validated in
     `__init_subclass__` (seeder-style: non-empty, unique entry names, unique
     schedule keys), `name_verbose`, and a stable per-entry `schedule_key`.
   - done when: a subclass with valid entries constructs; missing/duplicate/invalid
     entries raise `ValueError` (unit tests).

2. `CelerySchedulerTask` model + migration 0010
   - Fields: `schedule_key` (unique), `display_name`, `crontab` (string, for
     observability), `last_sent_datetime`, `claimed_by` (hostname:pid of last
     claimer). Plain model like `CeleryTask`; db_table
     `django_spire_celery_scheduler_task`; read-only admin (list_display of
     schedule_key, display_name, last_sent_datetime, claimed_by).
   - done when: `just make-migrations` generates 0010 and `just migrate` applies.

3. Claim service (riskiest step)
   - `claim_schedule_slot(entry, now, claimed_by) -> CeleryTask | None` in
     `scheduler.py`: reads/creates the row, does the due check + atomic claim
     from the mechanism above, and on winning claims sends via the entry's
     manager. Per-entry exceptions are caught and logged, never propagated.
   - done when: unit tests prove single-winner, no second claim on the same slot,
     stale-gap fires exactly once (no replay), first run does not fire
     retroactively, and 8 threads racing one slot produce exactly one send
     (manager send monkeypatched to count).

4. Scheduler thread + registry
   - `scheduler.py`: module-level singleton with `threading.Event`;
     `start_scheduler()` / `stop_scheduler()`; loop waits on the event for the
     tick interval, `close_old_connections()` per tick, iterates every entry of
     every registered scheduler class (imported from
     `DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES` via `import_string`).
   - Start guards in `CeleryConfig.ready()`: enabled setting, non-empty classes
     list, `RUN_MAIN != 'false'` (skip the runserver reloader parent), thread not
     already started. Daemon thread, named `django-spire-celery-scheduler`.
   - done when: with `override_settings(enabled=True, classes=[...])` and an
     advanced fake clock, the scheduler sends a due task exactly once and stops
     cleanly (test); disabled setting or `RUN_MAIN=false` starts no thread (test).

5. Test project wiring
   - `test_project/app/celery/scheduler.py`: `TestProjectScheduler(CeleryScheduler)`
     with entries reusing existing managers (e.g. `PirateSongCeleryTaskManager`,
     `crontab='*/5'`, `kwargs={'length': 2}`) plus a second entry.
   - `base_settings.py`: `DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES = [...]`,
     `DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED = True`.
   - `test_settings.py`: `DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED = False` (explicit
     guard, comment styled after the existing metric guard).
   - done when: `just run-server` logs the scheduler starting, and a due slot
     creates exactly one `CeleryTask` row.

6. Full test pass + lint
   - `django_spire/celery/tests/test_worker.py` (new) covering steps 1-4 plus an
     import/registration test for `TestProjectWorker`.
   - done when: `just test-app django_spire/celery`, `just test`, `ruff check .`,
     `ruff format --check .` all green.

7. Docs
   - AGENTS.md: new "Scheduler" subsection in the Celery section (class usage,
     settings, exactly-once claim, no retroactive catch-up, RUN_MAIN/test guards,
     celery-app-in-web-process requirement) and rows for the three new settings.
   - done when: AGENTS.md reflects the feature and this plan doc is committed.

## Risks / notes

- Riskiest step is 3 (concurrency correctness); mitigated by the 8-thread race
  test and by the claim being one plain atomic UPDATE (portable, no locks to
  reason about).
- Schedules are evaluated in the celery app's timezone (default UTC, same as
  robit's default unless configured).
- `BaseCeleryTaskManager.send_task` already requires the project celery app to be
  registered in the web process (`test_project/__init__.py`); the worker adds no
  new requirement.
- Out of scope (noted for follow-up): migrating `test_project/worker.py` robit
  jobs, dynamic kwargs callables, per-entry queue override, metrics for sends,
  `worker.py` replacement of robit.

## Deviations

1. Renamed from worker to scheduler
   - `CeleryWorker` / `django_spire.celery.worker` became `CeleryScheduler` /
     `django_spire.celery.scheduler`; entry `SchedulerTask`, model
     `CelerySchedulerTask`, settings `DJANGO_SPIRE_CELERY_SCHEDULER_*`, test
     project `TestProjectScheduler` in `test_project/app/celery/scheduler.py`.
   - The class only enqueues sends at cron time and never executes task code,
     so "worker" collided with celery's worker (executor) vocabulary and
     mislabeled the behavior; user requested the rename before approval.
2. Lint completion criterion scoped to touched files
   - The repo baseline already fails `ruff check .` with ~1060 pre-existing
     errors (manager.py, tools.py, factories, templatetags, ...).
   - Completion test now requires zero new issues on the files this plan
     touches; all new files are fully lint- and format-clean.
3. `claimed_by` uses `default=''` instead of `null=True`
   - New code should not add `DJ001` debt; empty string means "no claimer yet".
4. `apps.py` imports `start_scheduler` inside `ready()` (noqa: PLC0415)
   - A module-level import makes `apps.py` pull `scheduler -> manager ->
     models` while the app registry is still populating (AppRegistryNotReady).
     Function-local import matches the existing `tools.py` pattern.
5. Migration 0010 excludes an unrelated pending `AlterModelOptions` for
   `CeleryTask`
   - The user's latest commit changed `CeleryTask.Meta` without a migration;
     `makemigrations` picked it up alongside the new model. Kept the migration
     to only `CreateModel(CelerySchedulerTask)`; the pending Meta change is
     left for the user's own commit.
6. Fixed the stale `test_ordering_default` assertion
   - The user's commit 02d510d1 changed `CeleryTask.Meta.ordering` to
     `('-queued_datetime',)` without updating the test (it still asserted
     `('-started_datetime',)`), failing the full suite independently of this
     work. Updated the test to match the model Meta so the suite is green;
     flagging in case the model change was not intended.
7. Thread tests got per-test scheduler classes
   - The full suite runs 12 xdist workers against one shared test DB; three
     thread tests originally shared one row key (and fake clock), so parallel
     workers raced each other's claims and the loop test flaked. Each thread
     test now uses its own module-level scheduler class with a unique entry
     name/row key; claim tests already used uuid names.

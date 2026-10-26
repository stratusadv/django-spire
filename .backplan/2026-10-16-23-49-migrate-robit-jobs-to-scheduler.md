# Migrate robit cron jobs to the embedded Celery scheduler — 2026-10-16-23-49

Status: Executed

## End state
The two cron jobs that `test_project/worker.py` ran via the separate robit process
(`Process Ready Notifications` and `Convert Files to Model Objects`, both `0 0 * * 6`)
now run through the embedded `CeleryScheduler` (beat-style: the web claims the slot and
sends to the broker; the worker pool executes). `TestProjectScheduler.tasks` holds 4
entries with unique schedule keys, and the pending `CeleryTask` Meta migration is
generated and applied so `makemigrations --check` reports no changes.

## Completion test
- `just python -m pytest django_spire/celery/tests/test_scheduler.py --reuse-db` passes,
  including the updated registration test asserting 4 entries.
- `just test` (full suite) passes.
- `ruff check` + `ruff format --check` clean on all touched files.
- `just python manage.py makemigrations --check --dry-run` prints "No changes detected".

Observed: scheduler module `27 passed`; `just test` full suite `4523 passed, 0 failed`;
`ruff check` + `ruff format --check` clean on the four touched .py files (the generated
migration is excluded from lint by `ruff.toml` `*/migrations/*`); `makemigrations --check`
-> "No changes detected"; `migrate django_spire_celery` applied 0011 OK.

## Current state
- `108f74bf` (committed) set `CeleryTask.Meta.ordering = ('-queued_datetime',)` with no
  migration; `makemigrations --check` reported exactly one pending:
  `0011_alter_celerytask_options` (Change Meta options on celerytask).
- `test_project/worker.py` (separate process, `python test_project/worker.py`) registers
  two robit jobs at `0 0 * * 6`:
  - `Process Ready Notifications` -> `notification_automations.process_notifications()`
  - `Convert Files to Model Objects` -> `Entry.services.automation.convert_files_to_model_objects()`
- Committed scheduler (`be6f9e1a`) sends via `BaseCeleryTaskManager.send_task`; the demo
  tasks/managers live in `test_project/app/celery/celery/tasks.py` + `managers.py`;
  `TestProjectScheduler` currently has 2 entries (Pirate Song, Ninja Attack).
- Verified: constructor `__get__` (django_spire/contrib/constructor/constructor.py:52)
  means `Entry.services.automation.convert_files_to_model_objects()` works with a blank
  instance — the exact call robit already makes.
- Verified: `celery_task(name, meta_data_model, update_interval_seconds, **task_opts)`.
- `.backplan/` is gitignored (`.gitignore:20`).

## Plan
1. Generate the pending migration.
   - done when `makemigrations` writes `0011_alter_celerytask_options.py`, `--check` is
     clean, and `migrate django_spire_celery` applies it.
2. Add the two robit-replacement celery tasks to `test_project/app/celery/celery/tasks.py`.
   - thin `@celery_task()` wrappers: `process_ready_notifications_task` ->
     `notification_automations.process_notifications()`,
     `convert_files_to_model_objects_task` ->
     `Entry.services.automation.convert_files_to_model_objects()`.
   - done when both are importable and delegate to the existing service call.
3. Add the two managers to `test_project/app/celery/celery/managers.py`.
   - done when both reference the new `task_name` and set a `display_name`.
4. Register the two entries in `TestProjectScheduler` at crontab `0 0 * * 6`.
   - done when `TestProjectScheduler.tasks` has 4 entries with unique schedule keys.
5. Update the registration test to expect 4 entries.
   - done when `TestProjectSchedulerRegistration` asserts `len == 4`.
6. Run tests + ruff.
   - done when the celery test module and full suite pass and ruff is clean on touched files.
7. Commit the migration + robit migration together.
   - done when a single commit lands both.

## Deviations
1. `test_project/worker.py` left untouched (robit process not removed).
   - what: the robit worker file keeps its two job registrations.
   - why: removing user-owned infrastructure is a decision to leave to the owner; the two
     Saturday jobs would double-fire only if robit and the web scheduler are both running,
     which the user controls. Flagged in the report.
2. Split into two commits (migration, then robit migration) instead of one.
   - what: the missing `0011` Meta-ordering migration is committed separately from the
     robit->scheduler feature.
   - why: the migration closes a loose end left by `108f74bf` and is a distinct, revertable
     change from the feature; the report references both.
3. Pre-existing flaky test found, not fixed: `test_admin_smoke.py::
   test_every_change_form_loads`.
   - what: intermittently fails with `EOFError: Ran out of input` when the admin factory
     seeds a CeleryTask with `state=FAILURE` and `_result=b''` and `has_exception_result`
     runs `pickle.loads(b'')`.
   - why left alone: unrelated to this change; root cause is `_celery_state_choices()`
     iterating the `states.ALL_STATES` frozenset, so the factory's "first choice" state is
     non-deterministic across `PYTHONHASHSEED`. Confirmed: seeds 9/13/30 fail, 38/41 pass.
     Flagged for the owner to fix (guard `pickle.loads` or stop the factory seeding
     FAILURE with an empty result).

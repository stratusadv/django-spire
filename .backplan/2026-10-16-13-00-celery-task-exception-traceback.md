# celery task exception traceback — 2026-10-16-13-00

Status: Executed

## End state

When a celery task fails, the full formatted exception traceback is stored in a
dedicated `exception_traceback` column on the `CeleryTask` record (named after
the model's existing `exception_*` vocabulary: `exception_result`,
`has_exception_result`), populated by every
capture path that has a trace, rendered on the `CeleryTaskAdmin` change page
and on the test_project celery home page, and the behavior is covered by tests
in `django_spire/celery/tests/`.

## Completion test

1. `just test-app django_spire/celery` passes, including new tests proving:
   - FAILURE via native backend capture (`async_result.traceback`)
     → `celery_task.exception_traceback` is populated.
   - FAILURE via the final-meta repair path (`_build_final_exception_result`)
     → `celery_task.exception_traceback` is populated from tracker meta
     `error_traceback`.
   - SUCCESS terminal → `celery_task.exception_traceback` is `None`.
   - `tracker.finish(states.FAILURE, exc=...)` → `tracker.meta.error_traceback`
     is the formatted exception text.
2. `just python manage.py makemigrations --check --dry-run` exits clean
   (migration for the new field exists).
3. `ruff check` and `ruff format --check` are clean on touched files.

## Current state

Verified facts (2026-10-16):

- `CeleryExceptionResult` (django_spire/celery/result.py:26)
  - fields: `exc_type`, `message`, `traceback` (str | None), `_einfo_pickle`
  - `__str__` = `'{exc_type}: {message}'` (no trace)
  - stored pickled in `CeleryTask._result` (BinaryField) on FAILURE
- Capture is web-side, in `CeleryTaskService` (django_spire/celery/services/service.py):
  - `_capture_exception_result` (service.py:84) — reads
    `async_result.traceback`, re-raises via `async_result.get()` to recover the
    exception; used when the backend main row is FAILURE (service.py:112)
  - `_build_final_exception_result` (service.py:166) — builds
    `CeleryExceptionResult(Exception(message), None, None)` from the tracker
    final-meta row; **traceback is always None here** (the gap)
  - `_apply_terminal_snapshot` (service.py:264) — `meta.set_failed(error)`,
    `new_result = pickle.dumps(exception_result)`; no trace column written
  - `_save_snapshot` (service.py:316) — full `fresh.save()`, so any field set
    on `fresh` persists
- `async_result.traceback` is real in celery 5.6.3: a property returning
  `self._get_task_meta().get('traceback')` (verified against installed source)
- Worker side:
  - `CeleryTaskTracker.finish(states.FAILURE, exc)` (tracker.py:142) calls
    `meta.set_failed(f'{type(exc).__name__}: {exc}')` — **never captures the
    traceback**, even though the live exception is in hand
  - final meta is pushed to the derived key
    (`derive_final_meta_key`, meta.py:16) via `_push_final_meta` (tracker.py:236)
    and read web-side by `_read_final_meta` (service.py:135)
- `CeleryTaskMeta` (meta.py:23) has `error: str | None` and
  `failed_time: float | None`; no traceback field
- `CeleryTask` model (models.py:20): no traceback column; existing raw-storage
  convention is underscore fields (`_result`, `_task_meta`) with properties;
  `exception_result` property (models.py:105) currently has no callers
- Display:
  - `CeleryTaskAdmin` readonly_fields already ends with `result_verbose`,
    `exception_result` (admin.py)
  - framework task UI templates do not render exception info
  - test_project `celery_home_view` (test_project/app/celery/views.py) has a
    `check_task_id` branch that populates `context['task_data']` etc.; the
    home page `dl` (test_project/templates/celery/page/home_page.html:92-109)
    shows Info/State/Result/Data rows, no traceback
- Working tree already carries a failing demo task (`lizard_fail_task`,
  ZeroDivisionError) wired to the home page and a
  `LizardFailCeleryTaskManager` — useful for manual verification
- Migrations exist up to `0007_merge_20261015_0950` in
  django_spire/celery/migrations/
- House style: ruff (ALL, single quotes, 100 cols), no comments,
  `just` for all commands, tests in `django_spire/celery/tests/`
  (test_services/test_celery_task_service.py, test_tracker.py, test_models.py,
  test_admin.py)

## Plan

1. Model column + migration
   - Add `exception_traceback = models.TextField(null=True, blank=True, verbose_name='Exception Traceback')`
     to `CeleryTask`; run `just make-migrations` and `just migrate`.
   - done when the migration adds the field and
     `just python manage.py makemigrations --check --dry-run` is clean.
2. Worker-side capture (tracker + meta)
   - Add `error_traceback: str | None = None` to `CeleryTaskMeta` (next to
     `error`/`failed_time`).
   - In `CeleryTaskTracker.finish`, on FAILURE with `exc` not None, format the
     exception (`traceback.format_exception`) and store it in
     `self.meta.error_traceback` alongside `meta.set_failed(...)`, so the
     final-meta push carries it.
   - done when a `test_tracker.py` test proves `finish(FAILURE, exc)` leaves a
     formatted trace in `tracker.meta.error_traceback`.
3. Web-side population (single writer) + capture-gap fix
   - `_build_final_exception_result`: pass
     `final_meta_dict.get('error_traceback')` as the traceback text.
   - `_apply_terminal_snapshot`: on FAILURE set
     `fresh.exception_traceback = exception_result.traceback`; on SUCCESS/RETRY
     set `fresh.exception_traceback = None`; mirror `self.obj.exception_traceback`
     in `_save_snapshot`.
   - done when service tests show the column populated on both FAILURE paths
     and `None` after SUCCESS.
4. Display: admin + test_project home page
   - Add `exception_traceback` to `CeleryTaskAdmin.readonly_fields`.
   - In `celery_home_view`'s `check_task_id` branch, expose the failed task's
     trace in context (`exception_traceback`); render it in the home page `dl`
     (monospace block).
   - done when the admin change page and the home page show the full traceback
     for a failed task (admin assertion test + home page row visible).
5. Tests, lint, docs
   - Add/adjust tests in test_services, test_tracker, test_models (and
     test_admin if a readonly-list pattern exists); run
     `just test-app django_spire/celery`.
   - `ruff check` / `ruff format` on touched files.
   - Update the AGENTS.md Celery section: one line on the new column and the
     tracker meta `error_traceback` field.
   - done when the celery app suite is green, ruff is clean, AGENTS.md is
     accurate.

Risky step: 3 — it touches the single-writer terminal path
(`_apply_backend_snapshot` / state machine / metric firing) and depends on the
backend actually carrying the trace in the main-row meta; a wrong assumption
here silently leaves the column empty on one of the two FAILURE paths.

Naming note: the tracker meta field stays `error_traceback` (meta's own
vocabulary is `error` / `failed_time`); only the model column and the context
key use `exception_traceback`.

## Deviations

1. Migration 0008 bundles a pre-existing pending `task_id` AlterField
   - `just make-migrations` generated 0008 with both the new
     `exception_traceback` AddField and an `AlterField task_id` that was
     already pending in committed model state (no prior migration for it).
   - Kept rather than split: it is unrelated but was already un-migrated;
     splitting it would not change behavior, and both apply cleanly.
2. Field switched from `null=True` to `blank=True, default=''`
   - `ruff` (select ALL) flags the new column with DJ001 (no `null=True` on
     string fields); the only pre-existing violation in models.py is the same
     rule on `model_key`.
   - New fields follow the enforced rule: empty string means "no trace";
     service/tests updated to match (`== ''` instead of `is None`).

## Completion

Observed output (2026-10-16):

- `just test-app django_spire/celery` → `297 passed` (parallel, fresh test DB)
- `just python manage.py makemigrations --check --dry-run` → `No changes detected`
- `ruff format --check django_spire/celery/ test_project/app/celery/` →
  `53 files already formatted`; `ruff check` on touched files shows no
  violations on new lines (remaining app debt is pre-existing)
- Home page template compiles via `get_template('celery/page/home_page.html')`

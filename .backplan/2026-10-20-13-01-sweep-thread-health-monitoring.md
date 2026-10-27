# Sweep thread health monitoring — 2026-10-20-13-01

Status: Executed

## End state

An unexpected sweep-loop death logs an ERROR with its traceback
(distinguishable from a graceful `stop_sweep()`), the scheduler loop gets
the same treatment, and the `CeleryTaskSweep` claim row (`key`,
`last_swept_datetime`, `claimed_by`) is viewable in a read-only Django
admin exactly like `CelerySchedulerTask` is today — so an operator can
open the admin and see at a glance whether the sweep is advancing and
which instance last won.

## Completion test

```bash
just python -m pytest django_spire/celery/tests/ --reuse-db -q
# new tests:
#   crash: _sweep_loop whose loop scaffolding raises exits the thread and logs ERROR 'crashed' (caplog)
#   graceful: a normal stop logs INFO 'stopped' with no 'crashed' entry
#   scheduler: same crash/graceful pair for _scheduler_loop
#   admin: CeleryTaskSweep is registered read-only (no add/change/delete)
.venv/bin/ruff check <touched files>   # no NEW violations (tree is not lint-clean at HEAD)
```

## Current state

Verified facts:

- `_sweep_loop` (`django_spire/celery/sweep.py`): per-window
  try/except around the claim and the resolve (one bad window never kills
  the loop), `close_old_connections()` each iteration, and a `finally`
  that logs INFO `'Celery task sweep stopped'` — the SAME line for a
  graceful stop and for an unexpected death. There is no other death
  signal: an uncaught exception kills the thread silently apart from that
  indistinguishable INFO line.
- Thread liveness (`_STATE.thread.is_alive()`) is referenced only inside
  `start_sweep`/`stop_sweep`; nothing exposes it — no admin, no endpoint,
  no metric, no watchdog, no restart-on-death.
- The de-facto health signal already exists in the data: a healthy setup
  claims a window every `DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS`, so
  `CeleryTaskSweep.last_swept_datetime` advances every interval (by
  whichever instance wins) and `claimed_by` records the winning
  `host:pid`. Staleness beyond one interval means no instance is
  sweeping.
- `CelerySchedulerTask` is registered read-only in the admin
  (`django_spire/celery/admin.py:49-69`: `list_display` includes
  `last_sent_datetime` + `claimed_by`, all fields readonly,
  add/change/delete denied) — the exact template to mirror.
  `CeleryTaskSweep` is not registered anywhere.
- The scheduler loop has the identical death-log gap
  (`scheduler.py` finally logs INFO `'Celery scheduler stopped'`
  unconditionally).
- `test_admin.py` contains an admin smoke suite that loads every
  registered model's change form, so a new registration is covered
  automatically once added.

## Plan

1. Distinguish death from graceful stop in the logs (sweep + scheduler parity)
   - Wrap the `while` loop bodies of `_sweep_loop` and `_scheduler_loop`
     in `try/except Exception → logger.exception('... loop crashed ...')`
     ahead of the existing `finally` (which keeps logging the INFO
     stopped line).
   - done when crash tests show an ERROR with traceback and the thread
     exited, and graceful-stop tests show no 'crashed' entry.
2. Read-only admin for `CeleryTaskSweep`
   - Register in `django_spire/celery/admin.py` mirroring
     `CelerySchedulerTaskAdmin`: `list_display = ('key',
     'last_swept_datetime', 'claimed_by')`, all readonly, add/change/
     delete denied.
   - done when the registration test passes and the admin smoke suite
     still loads every change form.
3. Verify
   - Celery suite + ruff on touched files.
   - done when green.

Out of scope (noted as follow-up options, not built):
- A watchdog that restarts a dead thread in-process.
- A staleness metric/management command (e.g. fail when
  `last_swept_datetime` is older than N intervals) for external alerting.

## Deviations

- Crash tests use `caplog.at_level(logging.INFO, ...)` (not ERROR) so both
  the ERROR `'crashed'` and the INFO `'stopped'` records are captured; at
  ERROR level the graceful INFO line the test also asserts on would be
  filtered out by the logger.
- `ruff check` on `admin.py` reports 3 `ARG002` (unused `request`) that
  pre-exist at HEAD (in `CeleryTaskStateFilter`/`CeleryTaskAdmin`); the new
  `CeleryTaskSweepAdmin` methods use `_request`/`_obj` and add none.

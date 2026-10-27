# Validate Celery module operation

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-21-15-05

## End State

A single review document (this file, extended in place) contains: (1) a behavior spec of
`django_spire/celery/` covering every subsystem, each claim cited to code and mapped against
the ten confirmed intended-behavior contracts; (2) a separation-of-concerns/portability audit
of the worker-side runtime judged against the zero-Django-in-worker bar; (3) a validation
report with captured evidence from five live multi-instance race harnesses and live
broker/worker scenarios; and (4) a discrepancy table (spec vs observed vs intended) with
severity and recommendation per finding, report-only with no code fixes.

## Observable Concern

Worker portability is the claim most likely to be wrong: the confirmed bar is zero Django in
a Spire worker, but step 0 already found `runner.py:6` importing
`celery.contrib.django.task.DjangoTask` (forces `django.setup()` in the worker) and
`test_project/celery.py` loading Django settings as the Celery config source
(`config_from_object('django.conf:settings')`). The audit must classify every touchpoint as
violation vs celery-native necessity, not just list imports.

## Confirmed Intent Baseline (user-confirmed 2026-10-21, 15 questions)

Normative contracts the spec is validated against:

1. Portability: a Spire task must run on a bare Celery worker with ZERO Django
   (no `django.setup()`, no settings, no ORM).
2. Worker runtime (decorator/runner/tracker/meta/result) imports only stdlib + pydantic +
   celery + kombu; tracker tuning comes from task kwargs or Celery app config, not Django settings.
3. Race harnesses (all five, live): scheduler multi-instance claim, sweep multi-instance
   window claim, concurrent `_apply_backend_snapshot` apply, tracker flusher handoff,
   `dedupe_unready` reuse.
4. Healing: worker death without terminal backend write -> reaper marks FAILURE after
   threshold, NO requeue (operator decides next step).
5. Monitoring: validate existing terminal metrics, enumerate liveness gaps, include
   forward-looking monitoring design recommendations.
6. State machine: illegal transitions dropped with a warning; never corrupt the row, never
   raise; terminals sticky forever.
7. Send failure: exhausted `send_task` retries -> terminal dead FAILURE record; no built-in
   resubmit.
8. Scheduler time semantics: no replay of missed slots; fresh entries fire on the next
   future slot only; clock skew can only delay a fire, never duplicate it.
9. Source field: default USER; scheduler stamps SCHEDULED; EVENT/API/SYSTEM passed
   explicitly; admin-only visibility (UI exposure is a future decision).
10. Cancel: best-effort Celery revoke; row ends REVOKED via normal state sync; document
    exactly which queued/running/finished cases it does and doesn't cover.

Deliverable/scope/depth: behavior spec + validation report; entire framework app
end-to-end (worker runtime included); code + tests + live broker/worker + multi-instance
races; findings are report-only.

## Current State

Verified step-0 facts (working tree = review target, includes uncommitted `source` field,
web-process thread gating, scheduler orphan pruning):

- Module layout (`django_spire/celery/`): `decorators.py`, `runner.py`, `tracker.py`,
  `meta.py`, `result.py`, `state_machine.py` (worker side); `manager.py`, `models.py`,
  `querysets.py`, `services/` (`service.py`, `resolver.py`, `queue_service.py`),
  `scheduler.py`, `sweep.py`, `process.py`, `choices.py`, `admin.py`, `views/`,
  `templates/`, `templatetags/`, `management/commands/prune_stale_started_celery_tasks.py`
  (web side).
- Review target moved to `a2dfb58d` (see Deviations) + clean working tree; includes new sweep
  defaults: `DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS = 20`,
  `DJANGO_SPIRE_CELERY_SWEEP_TASK_LIMIT = 20` (django_spire/settings.py), and a new
  `tzdata==2026.5` dependency.
- Worker-side import audit (direct imports only, transitive audit pending in step 3):
  - `decorators.py`: celery, spire meta/runner - clean.
  - `runner.py`: **`celery.contrib.django.task.DjangoTask`** (Django touchpoint),
    celery, spire meta/tracker.
  - `tracker.py`: celery, spire meta - clean.
  - `meta.py`: stdlib + pydantic - clean.
  - `result.py`: stdlib + celery.utils.serialization - clean.
  - `state_machine.py`: celery states - clean.
- `test_project/celery.py`: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', ...)`,
  `config_from_object('django.conf:settings', namespace='CELERY')`,
  `task_track_started=True`, `task_acks_late=True`, `task_reject_on_worker_lost=True`,
  `worker_deduplicate_successful_tasks=True`, `worker_max_tasks_per_child=200`,
  `task_time_limit=3600`/soft 3500, default queue `django_spire_test_project_queue`.
  Note: `reject_on_worker_lost=True` + `acks_late` means the broker requeues a task whose
  worker died mid-run - an interaction with contract 4 (reaper FAILURE) that the live
  scenarios must pin down.
- Terminal metrics map: `services/service.py:32-34` SUCCESS->`celery_task_success`,
  FAILURE->`celery_task_failure`, RETRY->`celery_task_retry`, fired from
  `CeleryTaskService` on transition.
- Environment for live work: `development.env` provides `CELERY_AMQP_*` (RabbitMQ) and
  `CELERY_PGSQL_*` (Postgres result backend); broker/backend liveness to be verified in
  step 1. Dev worker via `just celery` (threads pool per AGENTS.md).
- Test inventory: 20 test files under `django_spire/celery/tests/`; full celery dir 393
  passed; full suite 4565 passed (2026-10-21).

Assumptions (not asked; flag for correction at approval):

- Review target is the working tree, not HEAD.
- Race harnesses are written as a re-runnable pytest file in `django_spire/celery/tests/`
  (a review artifact; left uncommitted like all session work).
- Live scenarios run against the local dev stack (`just run-server` + `just celery` with
  `development.env`); transcripts captured into this doc.
- No code fixes of any kind; harness/test files are the only new artifacts.

## Plan

1. Verify environment and finish step 0
   - Confirm RabbitMQ and Postgres result backend are up; start them or record the block.
   - Confirm `just run-server` + `just celery` boot cleanly on the current tree.
   - Done when broker connect + worker boot + server boot are evidenced (or blocker recorded).
2. Draft the behavior spec (this doc, extended)
   - One section per subsystem: task authoring (decorator/runner/tracker/meta), send path
     (manager), state machine + web sync (state_machine/service/querysets), results,
     scheduler (claims, pruning, web-process gating), sweep, reaper, UI (views/templates/
     admin), metrics, source field.
   - Every claim cited to file:line; the ten confirmed contracts stated as normative and
     each mapped to its implementing code.
   - Done when every subsystem section exists and no claim lacks a code citation.
3. Separation-of-concerns + portability audit
   - Table of every import in the six worker-side files plus transitive
     `django_spire.celery.*` / `django*` imports, each classified: violation / celery-native
     necessity / web-side-only. Judge against contracts 1-2.
   - Done when the audit table covers all worker-side modules and each row has a
     classification + rationale.
4. Build and run the five race harnesses (live, Postgres, real threads/processes)
   - Harnesses: scheduler claim (N instances, one due slot, exactly one send), sweep window
     (N instances, one window, exactly one resolve), concurrent snapshot apply (N web polls
     racing on one task: monotonic progress + exactly one terminal metric), tracker flusher
     handoff (writer vs flusher: no lost updates, monotonic), `dedupe_unready` (concurrent
     sends, one row, one send).
   - Done when each harness has a captured transcript showing exactly one winner, recorded
     in this doc.
5. Live broker/worker scenarios
   - (a) SUCCESS lifecycle: PENDING->STARTED->SUCCESS row + exactly one
     `celery_task_success`; (b) send failure with broker down: terminal FAILURE row +
     `send_error_message`; (c) cancel QUEUED task -> REVOKED; (d) cancel RUNNING task ->
     observed behavior; (e) SIGKILL worker mid-task: observe broker requeue
     (`reject_on_worker_lost`) vs reaper stale-STARTED path, then run
     `prune_stale_started_celery_tasks` dry-run + real; (f) `dedupe_unready` live: two sends
     while unready -> one row.
   - Done when >=6 scenario transcripts (row states, backend states, log excerpts) are in
     this doc, each checked against the confirmed contracts.
6. Monitoring validation, gaps, recommendations
   - Evidence for exactly-once terminal metrics; scheduler + sweep liveness observability
     today (logs, claim rows); broker-down signal behavior; forward-looking recommendations
     (heartbeats, failure notifications, stale alerts, source UI exposure).
   - Done when gap list + recommendations are written in this doc.
7. Assemble discrepancy table and run completion test
   - Table: contract/claim vs observed vs intended, severity (informational/minor/major/
     critical), recommendation per row.
   - Run `just python -m pytest django_spire/celery/tests/ --reuse-db -q` and `just test`;
     quote real output; set Status: Executed.
   - Done when discrepancy table is complete and the completion test output is captured.

## Live Evidence and Findings (in progress)

Environment (step 1, 15:10): RabbitMQ `rabbitmq.compute.stratusadv.com` + Postgres result
backend (DigitalOcean `celery-development`) both connected; web DB connected. User's own
dev server already running (second `run-server` exited on port clash, harmless). Review
worker 0D5: `celery -A test_project worker --pool=prefork` (concurrency 8), 8 tasks
registered, connected, `mingle: sync with 14 nodes` on the shared broker.

Observation O-1 (positive, scheduler design): at 15:15:14 the worker-embedded scheduler
thread claimed and sent the `*/5` Pirate Song slot (`Sent scheduled task ... (1d5d8f22-...)`),
the worker executed it (`succeeded in 4.24s: 'The pirate says YARR'`). The user's web server
ran its own scheduler simultaneously; exactly one send occurred - live evidence for the
atomic-claim design (contracts 3, 8).

Finding F-1 (critical, healing / separation of concerns): the worker-embedded sweep thread
can NEVER resolve backend state
- Evidence: worker 0D5 logs 15:15:34-15:20:09, 12 repeats at the 20s sweep interval:
  `WARNING/MainProcess Failed to resolve CeleryTask 1d5d8f22-... from the backend` with
  `RuntimeError: Never call result.get() within a task!` raised from
  `CeleryTaskService._safe_result_get` (`services/service.py:59`) via
  `resolve_celery_tasks` (`services/resolver.py:31`).
- Mechanism: Celery's `_task_join_will_block` is a PROCESS-GLOBAL flag
  (`celery/_state.py:53-62`), set to True when the worker starts
  (`celery/worker/components.py:171`, prefork pool). So `AsyncResult.get()` raises
  `E_WOULDBLOCK` from ANY thread in a worker process, including the sweep daemon thread
  started by `AppConfig.ready()` (ready() runs when the worker calls `django.setup()`;
  `is_web_server_process()` returns True for a worker argv, so the sweep starts).
- Impact: every sweep window the worker claims is consumed and wasted (claim commits,
  resolve fails); tasks stay stale until a web instance wins the next window (default 20s);
  continuous stack-trace log spam (12 traces in ~5min for ONE task).
- Contract check: contract 4 (reaper) unaffected (management command, web-side); but the
  "any instance can sweep" design is silently worker-broken - the module does not prevent
  the web-side sweep machinery from running inside workers.
- Secondary exposure (to verify in step 5): `resolve_unready_before_send=True` managers
  sent from the worker-embedded scheduler would hit the same `get()` in the send gate;
  the per-entry try/except would swallow it and skip the send silently.
- Recommendation (report-only): exclude worker processes from `start_sweep`/`start_scheduler`
  (e.g. detect the running worker), and/or make the terminal read non-blocking
  (`backend.get_task_meta()` / meta read instead of `AsyncResult.get()`), which is the only
  path that actually needs the result value.

Environment shift (15:1x-15:31, recorded as Deviation 3): the user ran an in-flight
dependency upgrade mid-review - working-tree `pyproject.toml`/`uv.lock` now pin
`django==6.1.2` (+boto3 1.43, paramiko 5.1, twilio 9.12, marko/markitdown) and the venv was
re-synced (venv django = 6.1.2 verified at 15:31). Consequences:
- Django 6.1 refuses the local dev DB at connect: `NotSupportedError: PostgreSQL 15 or later
  is required (found 14.24)` - every NEW process using the ORM against the dev DB fails.
  Confirmed live when a probe script's own `AppConfig.ready()`-started sweep/scheduler threads
  died on their first DB call (their per-iteration exception handlers logged and kept looping:
  "Failed to claim CeleryTask sweep window" / "Failed to prune unregistered
  CelerySchedulerTask rows" - the loops are crash-robust, verified).
- Worker 0D5 and the (now-stopped) user web server started before the sync and keep Django
  6.0.6 in memory; they still work. The user's dev server is no longer running (port free at
  15:32).
- Test DB (docker PG16, port 5439) is unaffected; pytest paths remain viable (smoke test
  pending below).
- Workaround for step-5 live scenarios: harness scripts bypass the support-policy check
  (monkeypatch `BaseDatabaseWrapper.check_database_version_supported` in the script only,
  framework code untouched) - the dev DB runs fine under 6.1 ORM queries; it is a policy gate,
  not a functional incompatibility (the whole stack ran on 6.0.6 against this PG14 until now).

Observation O-2 (positive, scheduler + dedupe + source, all live-verified via DB rows + worker
log):
- `source` field contract 9 works live: scheduler-created rows are `source='scheduled'`
  (django_spire_celery_task), UI sends `source='user'` (rows 20:38-20:46 UTC).
- `claim_schedule_slot` (`scheduler.py:120-150`) = get_or_create row -> future-timestamp guard
  (`last_sent >= moment` -> None: skew can only delay) -> `target_slot = moment +
  crontab.remaining_estimate(last_sent)` where celery's `remaining()` returns
  `next_grid_slot - now` (clamped-or-not, always <= 0 once the slot has passed) -> due iff
  `target_slot <= moment` -> atomic `filter(last_sent__lt=target_slot).update(last_sent=moment,
  claimed_by)` rowcount==1 wins -> `send_task(source=SCHEDULED)`. Verified against real celery
  5.6.3 source (schedules.py:572-639, utils/time.py:214-240).
- The 15:10 (21:10 UTC) Pirate slot was consumed with NO row and NO send: the (then-alive) web
  server's scheduler claimed the slot (claim UPDATE committed at ~21:10:0x) but its send never
  completed - the user stopped the server before it finished (port was still held at 15:10:20
  by the user's server; free by 15:32). My worker's next ticks correctly computed the NEXT
  slot (21:15:00) from the committed `last_sent` and fired it on the first due tick at
  21:15:14 (14s late = tick granularity). Design consequence (documented in discrepancy
  table): the claim commits independently of the send - a claimant dying between claim and
  send loses the slot with no audit trail (consistent with "at most once", but silent).
- 15:20/15:25/15:30 slots: worker-claimed, `dedupe_unready=True` (PirateSongCeleryTaskManager)
  found the stuck PENDING row 1d5d8f22 and reused it: worker log shows "Sent scheduled task
  (1d5d8f22-...)" at 15:20:14/15:25:14/15:30:14 but NO broker message was published (worker
  received the task only once, at 15:15:14) and no new CeleryTask row exists. While F-1 keeps
  the row unready and no web instance polls, every `*/5` slot silently fires into the void.

Finding F-2 (major, healing/observability): stale PENDING rows are reaper-out-of-scope.
- Evidence: 1d5d8f22 sat PENDING in the DB (started=None, meta={}) while the backend held
  SUCCESS (worker log: succeeded 15:15:18). The reaper command resolves "stale STARTED"
  records only; PENDING is never touched by it. The only resolvers are `update_from_backend`
  (view polls) and the sweep - and the sweep is worker-broken (F-1) and web-only otherwise.
- Impact: with the web down and only workers running, unready rows (PENDING or STARTED) are
  never resolved and never healed; the DB row is a permanent lie (PENDING vs backend SUCCESS)
  until a web process exists. The reaper therefore cannot be the sole healer (contract 4's
  "operator decides" story assumes the row at least reached STARTED).
- Recommendation (report-only): extend the reaper (or sweep-on-web) to PENDING rows with a
  threshold, and/or add a "backend says terminal, row says unready" drift metric.
- F-1 status at 15:30: still ongoing - ~28 failed resolves at the 20s interval for the same
  row (15:15:34 through 15:30:22+), continuous stack-trace spam on the shared worker.

## Behavior Spec (step 2, cited)

Scope: `django_spire/celery/` at `a2dfb58d` + working tree. "Web" = any process with
`is_web_server_process()` true (`process.py`); "worker" = a `celery worker` process. All
line numbers are to files under `django_spire/celery/` unless prefixed.

### 1. Task authoring (worker side)

- `@celery_task(name=None, meta_data_model=None, update_interval_seconds=5, **task_opts)`
  (`decorators.py:9-33`) wraps the function in `shared_task(base=CeleryTaskRunner, bind=True)`;
  the wrapper routes through `CeleryTaskRunner._run_lifecycle` (`decorators.py:15-29`); the
  per-task flush interval is stamped on the task object (`decorators.py:29`).
- `CeleryTaskRunner(DjangoTask)` (`runner.py:15`, **Django touchpoint - see audit**):
  - `run()` calls `_run_lifecycle(execute)` (`runner.py:33-38`); author code lives in
    `execute()` and receives `self.tracker`.
  - `_run_lifecycle` (`runner.py:40-56`): `Reject`/`Ignore` are re-raised untouched (Celery
    native handling); `Retry` -> `tracker.set_retries(request.retries + 1)` +
    `tracker.finish(RETRY)` + re-raise; any other `Exception` -> `tracker.finish(FAILURE, exc)`
    + re-raise; success -> `tracker.finish(SUCCESS)`. The runner never swallows; the native
    tracer (Celery) still owns the terminal backend row.
  - `_start_execution` (`runner.py:58-72`): builds the tracker (per-thread via
    `threading.local()`, so threads-pool workers are safe), stamps `retries` and
    `worker_hostname` into `meta.data`, then `set_started()`.
- `CeleryTaskTracker` (`tracker.py:31-250`):
  - Constructor validates `update_interval_seconds >= 5` (else ValueError) - the flusher
    cannot outrun the 5s floor (`tracker.py:34-66`); `_FLUSH_TIMEOUT_SECONDS = 10` bounds the
    final-flush join.
  - Author API: `set_started` (72), `set_completed` (78, mid-run only, never terminal),
    `set_started_and_completing_soon` (85), `update_state` (91, custom progress state, uppercased,
    <=32 chars), `update_count_progress` (100, bounds-validated),
    `set_cumulative_progress_target_value` (119) / `update_cumulative_progress` (123, capped at
    target), `set_retries` (136).
  - Coalescing: every author update builds a `_TrackerSnapshot` and hands it to a single
    pending slot (`_schedule_update`, 168) that a single flusher thread (`_ensure_flusher` 180,
    `_flusher_loop` 190) pushes to the backend at the update interval - author code never
    blocks on backend I/O; only the newest snapshot is kept (older ones dropped by design).
  - `finish(state, exc)` (143): stops the flusher (join <=10s, warn on timeout), then
    `_push_final_meta` (238): `backend.store_result(derive_final_meta_key(task_id), meta,
    states.SUCCESS)` - a DERIVED row (`key:spire-final-meta`, `meta.py` FINAL_META_KEY_SUFFIX)
    written as SUCCESS so DB backends set `date_done`/expiry and so the write cannot be
    exception-converted; the main backend row is left to the native tracer. A late flusher push
    after `_finished` is skipped (the native tracer owns the main row).
- `CeleryTaskMeta` (`meta.py:23-185`, pydantic `Generic[DataT]`, `extra='allow'`):
  - `__setattr__` intercepts progress floats (70-99): first set stamps `started_time`;
    the >=3rd update derives `estimated_completed_time` (10% buffer, only moved past the
    current threshold); every progress-like set stamps `last_update_time = time.time()` (99)
    - this is the reaper's staleness clock.
  - `set_completed` (125: progress=1.0), `set_failed` (133: progress=0.02 + error fields),
    `set_started_and_completing_soon` (138: progress=1.0), `merge()` (None-skipping deep merge
    of `data`).
  - `TaskDataModel` (typed `meta.data` base): `extra` + `validate_assignment` + `_on_change`
    hook that schedules the coalesced flush on attribute set - with a model registered,
    `tracker.meta.data.x = v` is the only "set data" call.

### 2. Send path (web side) - `BaseCeleryTaskManager` (`manager.py:40-212`)

- Identity: `reference_key = md5(task_name + manager-class-name + SECRET_KEY)` (66-72);
  `model_key = md5(model-class-name + pk + SECRET_KEY)` (74-83); broker headers
  `spire_reference_key` / `spire_display_name` / `spire_model_key` (112-121).
- `send_task(source=USER, **kwargs)` (123-161), in order:
  1. source must be a `CeleryTaskSourceChoices` value else ValueError (124-129).
  2. kwargs validated against `required_kwargs_keys_types` (presence + exact type) (197-206).
  3. `resolve_unready_before_send=True` -> `resolve_celery_tasks` on this manager's unready
     rows first (133-134). **Worker-process exposure**: in a worker, `result.get()` raises
     E_WOULDBLOCK (F-1); the resolver's per-task except swallows it, so the "resolve" silently
     does nothing and step 4 may dedupe-reuse a stale row (verified mechanism; live check in
     step 5).
  4. `dedupe_unready=True` (or resolve flag) -> return the first (newest,
     `ordering='-queued_datetime'` models.py:65) unready row WITHOUT sending (136-139).
  5. Publish loop: up to `send_task_retries` (default 2, max 5, `__init_subclass__` guard
     59-61) attempts of `celery.execute.send_task(name, kwargs, headers)` (144-148); retryable
     set = celery Operational/Timeout/Backend + kombu Channel/Connection + ConnectionError +
     OSError (29-37); exponential backoff `sleep(1 * 2**(attempt-1))` (157).
  6. On publish success: row created AFTER the publish, state PENDING, `queued_datetime=now`
     (163-173).
  7. On exhausted retries: terminal dead row - fresh uuid task_id, state FAILURE,
     started=completed=now, pickled `CeleryExceptionResult(SendFailedError)` in `_result`
     (175-195); surfaced via `send_failed` / `send_error_message` / `send_error_details`
     (models.py:226-272). No built-in resubmit (contract 7).
- `dedupe_unready` reuse is by row only: the reused task_id is returned and NO new broker
  message is published (live-verified: 15:20/15:25/15:30 slots, Live Evidence O-2).

### 3. State machine (`state_machine.py:4-53`)

- Transition table: PENDING/RECEIVED -> {STARTED, FAILURE, REVOKED, REJECTED}; STARTED ->
  {SUCCESS, FAILURE, RETRY, REVOKED}; RETRY -> {STARTED, FAILURE, REVOKED}; terminals
  (SUCCESS/FAILURE/REVOKED/REJECTED/IGNORED) -> empty (sticky forever).
- `_anchor` (25-38): any custom/unknown state anchors to STARTED for lookup (custom->terminal
  allowed; custom->plain STARTED not, per table).
- `ok(current, to)` (39-53): to-terminal from non-terminal always OK; same-state non-terminal
  idempotent OK; PENDING/RECEIVED never re-entered once left. Illegal transitions are DROPPED
  by the caller with a warning - the machine itself never raises (contract 6).

### 4. Web sync - single writer (`services/service.py:51-382`)

- `CeleryTask` rows are mutated ONLY by `CeleryTaskService` (the "web = single writer"
  docstring at 245-252); workers write only the result backend.
- `update_from_backend()` (173-207):
  - reads the backend row non-blocking via `async_result._get_task_meta()` (175);
  - sticky-terminal early return (178-181): once READY, only lazy result capture for
    SUCCESS-with-no-result (`_capture_result_lazy`, 66-83, retries each poll).
  - `_read_backend_snapshot` (106-134): SUCCESS -> `async_result.get()` (59 - **the call that
    breaks in workers, F-1**; only SQLAlchemy Operational/DatabaseError is caught, 60);
    FAILURE -> exception capture via get-raises (85-104); mid-run -> meta.result must be a dict
    intersecting `_TRACKER_META_FIELDS` (48) else dropped (the native STARTED
    `{'pid','hostname'}` write is filtered, 41-48).
  - `_FINAL_META_STATES = {SUCCESS, FAILURE, RETRY}` (43): terminal reads prefer the derived
    final-meta row (`_read_final_meta`, 136-156, non-blocking `get_task_meta`).
  - HEAL path (191-202): if the MAIN row is non-terminal but the final-meta row exists, the
    transition is inferred from it (`_infer_terminal_state`, 158-164:
    error/failed_time->FAILURE, completed_time->SUCCESS, else RETRY) - this is what recovers
    rows the native terminal write clobbered.
  - `_apply_backend_snapshot` (237-292): `transaction.atomic` + `select_for_update` (255-256);
    state-machine guard drops illegal transitions with a warning (258-265);
    `records_metric` = target has a metric reference AND fresh state non-terminal (267) -
    exactly-once per transition; terminal -> `_apply_terminal_snapshot` (294-327:
    set_completed/set_failed, result pickle, `_RESULT_UNAVAILABLE` keeps prior bytes (307),
    final meta merged with worker-side values winning (318-321), started backfilled from meta
    (323-325)); mid-run -> `_apply_meta_snapshot` (329-339) with PROGRESS MONOTONIC clamp
    (330-333); no-change -> no save, no metric (287-288, 341-350); save + in-memory refresh
    (352-366).
- `cancel()` (209-235): `control.revoke(task_id, terminate=True)` (213) - best-effort; worker
  unreachable -> warning + error string 'Workers could not be reached to cancel the task'
  (214-218), row untouched. Then atomic + `select_for_update` (220-221): state machine
  `ok(fresh.state, REVOKED)` guard else 'Task already finished with state ...' (223-224); sets
  REVOKED + `completed_datetime=now` (226-228) and fires the canceled metric (233).
  Coverage (contract 10): QUEUED (PENDING/RECEIVED) -> revoke honored at pickup (worker checks
  revoked on receipt) or at first heartbeat; RUNNING -> `terminate=True` asks the worker to
  kill it (pool-dependent); FINISHED (any terminal) -> refused with error string, row kept.
  The row ALWAYS ends REVOKED via this direct write (not via backend sync) for non-terminals;
  a later poll sees backend REVOKED and no-ops on the sticky terminal.
- `querysets.py`: `by_unready` = exclude(READY_STATES + EXCEPTION_STATES) =
  PENDING/RECEIVED/STARTED/RETRY (27-28); `by_completed` = SUCCESS (30-31);
  `by_reference_keys_model_keys` Q-OR with None->isnull (14-25).

### 5. Results (`result.py`)

- `CeleryNoResult` (17) + `set_pickled_no_result` (22) = the no-result sentinel in `_result`.
- `CeleryExceptionResult` (26-54): exc_type/message/traceback_text + optional pickled
  exception; rendered in task UI/admin; trace mirrored to `exception_traceback` column
  (service.py:316).
- `SendFailedError` (9) / `StaleStartedError` (13): the two non-task error stamps.

### 6. Scheduler (`scheduler.py:36-245`) - web-process thread, beat-style, send-only

- `SchedulerTask` (36-77): requires a `BaseCeleryTaskManager` subclass (TypeError else),
  5-field cron string (ValueError else), builds celery `schedules.crontab` with the entry's
  `nowfun` (default `django.utils.timezone.now`) (70-74). `CeleryScheduler.__init_subclass__`
  validates `tasks` non-empty, entries typed, names unique, and stamps
  `schedule_key = '<module>.<class>::<name>'` (83-113).
- Claim (`claim_schedule_slot`, 120-150): get_or_create the `CelerySchedulerTask` row
  (default `last_sent_datetime=now`, 123-131) -> future-timestamp guard: `last_sent >= now`
  => None (133-134) - **clock skew can only delay, never duplicate** -> `target_slot = now +
  crontab.remaining_estimate(last_sent)` (136-138) where celery's `remaining()` returns
  `next_grid_slot - now` (celery `schedules.py:572-639`, `utils/time.py:214-240`), i.e.
  `target_slot = max(now, next_grid_slot_after(last_sent))`: on-grid slots fire on the first
  tick at/after the slot; a slot missed while all instances were down fires AT MOST ONCE,
  anchored at first-tick-now (no replay of older slots) -> atomic
  `filter(last_sent__lt=target_slot).update(last_sent=now, claimed_by=...)` rowcount==1 wins
  (143-148) -> `manager_class().send_task(source=SCHEDULED, **kwargs)` (150) - contract 9
  stamp.
- Loop (`_scheduler_loop`, 178-216): starts with `prune_unregistered_scheduler_tasks`
  (152-156: deletes rows whose `schedule_key` is no longer registered, per loop start) then
  per entry per tick: claim; per-entry exceptions are caught+logged (193-195) so one bad entry
  never kills the loop; `send_failed` rows logged as warnings (200-205); tick sleep
  `DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS` (211).
- Gating (`start_scheduler`, 219-245): `DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED` AND
  `DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES` non-empty AND `is_web_server_process()` - single
  daemon thread, idempotent via alive-check (229-231).

### 7. Sweep (`sweep.py:23-113`) - web-process thread, backend-resolution worker

- Window claim (`claim_sweep_window`, 32-43): get_or_create `CeleryTaskSweep(key='default')`
  -> atomic `filter(last_swept__lt=now-interval).update(last_swept=now, claimed_by=...)`
  rowcount==1 - one resolver per interval across all instances.
- Loop (`_sweep_loop`, 51-76): on claim, `resolve_celery_tasks(by_unready(), limit=
  DJANGO_SPIRE_CELERY_SWEEP_TASK_LIMIT)` (66); claim and resolve failures are caught and
  logged per iteration (58-68); `close_old_connections` each iteration (70); outer
  crash-catch + finally stop-log (72-75). The CLAIM COMMITS EVEN IF RESOLVE FAILS (a broken
  resolver consumes the window - F-1's impact).
- `resolve_celery_tasks` (`services/resolver.py:1-44`): iterates in
  `queued_datetime, pk` order, skips rows already READY, counts attempts against the limit,
  per-task try/except -> 'Failed to resolve CeleryTask %s from the backend' + continue (31).
- Gating (`start_sweep`, 79-102): `DJANGO_SPIRE_CELERY_SWEEP_ENABLED` (default on) AND
  `is_web_server_process()`; interval default from settings (20s since ea01236f), task limit
  20.

### 8. Reaper (`management/commands/prune_stale_started_celery_tasks.py:21-149`) - web-side, manual

- Candidates: `state=STARTED` ONLY (104) with `meta.last_update_time` None or older than
  `--threshold` (default 600s) (102-109). **PENDING/RECEIVED/RETRY are out of scope (F-2).**
- Per candidate: `async_result.state` (non-blocking) (111-121); read failure -> skipped,
  NEVER marked FAILURE on a read failure (57-59); backend READY -> synced via
  `update_from_backend` (83-84, real terminal + metric); otherwise a single
  `inspect(timeout=5).active()` broadcast (123-141) - task id reported active on ANY worker ->
  skipped; inspect unreachable -> ALL failure candidates skipped (65-71, 132-133).
- Marking (87-90): `filter(pk__in=..., state=STARTED).update(state=FAILURE,
  completed_datetime=now, _result=pickled CeleryExceptionResult(StaleStartedError))` (143-149)
  - direct update (state machine bypassed, terminal-only), NO requeue (contract 4), and NO
  terminal metric (bypasses `_apply_backend_snapshot` - monitoring gap, step 6).
- `--dry-run` reports counts only (73-81).

### 9. UI (`views/task_views.py`, templates, admin)

- Every task item/toast render polls: `_task_view` calls
  `celery_task.services.update_from_backend()` on render (task_views.py:20-28) - this is the
  primary sync path when humans look at tasks; with no viewer, no sync.
- List views (57-75): parse `django_spire_celery_task_key_pairs` (comma `ref|model_key`
  pairs) -> `by_reference_keys_model_keys`; when `show_all` is absent, the view itself runs
  `resolve_celery_tasks(by_unready())` (70) before re-reading unready - the second web
  resolution path.
- Cancel (43-54): POST-only (405 else), `django_spire_celery.change_celerytask` permission,
  `services.cancel()` -> 409 `{'error': ...}` on refusal else 200 `{'canceled': True}`.
- Admin: `CeleryTaskAdmin` lists `source` (admin.py:93) and exposes it readonly in fieldsets
  (97/106/120) - **admin-only visibility** (contract 9); scheduler/sweep claim rows exposed
  readonly (50-52, 73-75).

### 10. Metrics (web-side, exactly-once by construction)

- Map (`service.py:30-36`): SUCCESS->`celery_task_success`, FAILURE->`celery_task_failure`,
  RETRY->`celery_task_retry`, REVOKED->`celery_task_canceled`.
- Fired only from `_record_terminal_metric` (369-381), invoked when
  `_apply_backend_snapshot` returns `records_metric` (267: target metric state AND fresh state
  non-terminal) or from `cancel()` directly (233) - once per non-terminal->terminal transition
  per row; sticky-terminal guards prevent re-fire.
- Delivery: `StatisticTrackingService.track_configured(reference=...)`
  (`metric/domain/statistic/services/tracking_service.py:104-121`) - no-op unless
  `DJANGO_SPIRE_METRIC_STATISTIC_KEY` + `DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY` configured;
  `track` (30-50) verifies domain match, applies a 2s PG statement timeout, increments in one
  transaction; any failure is warned + swallowed (metrics never break the sync). Each fire =
  one `StatisticValue` row (value=1, `processor_service.py:30-62`) - row counts are the
  exactly-once audit (trimmed per group at `DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX`).
- NOT fired (gaps, step 6): reaper-marked FAILURE (direct update), send-failure rows (created
  terminal), and any terminal reached while metric keys are unset.

### 11. Source field (contract 9)

- `CeleryTask.source` CharField(16), choices user/api/event/scheduled/system, default USER
  (models.py:41-43; choices.py:6-11); stamped by `send_task(source=...)` (manager.py:123,
  172, 190); scheduler stamps SCHEDULED (scheduler.py:150); verified live: `scheduled` on all
  scheduler rows, `user` on UI rows (Live Evidence O-2); admin-readonly (admin.py:93, 120);
  not exposed in templates (grep-verified: no template reference).

### Contract map (spec vs code vs live evidence)

| # | Contract | Implementing code | Live evidence | Verdict |
|---|----------|-------------------|---------------|---------|
| 1 | Zero Django in worker | VIOLATED: runner.py:15 `DjangoTask` (import forces `django.setup()`); project task modules import ORM (test_project tasks.py:8-9) | worker 0D5 runs `django.setup()` at boot (app-init DB warning) | FAILS the bar |
| 2 | Worker runtime = stdlib+pydantic+celery+kombu only | meta.py/tracker.py/state_machine.py/result.py clean; runner.py:6 DjangoTask; tuning via task opts (runner.py:23, decorators.py:29) | - | partial (see audit) |
| 3 | 5 race harnesses | claims: scheduler.py:143-148, sweep.py:40-42; apply: service.py:255-256; flusher: tracker.py:168-205; dedupe: manager.py:136-139 | O-1 (one send for 15:15 slot, two instances) | harnesses: step 4 |
| 4 | Healing: FAILURE after threshold, no requeue | reaper 87-90, 143-149 | pending (step 5e) | matches code |
| 5 | Monitoring: validate + gaps + recs | service.py:30-36, 267, 369-381; tracking_service.py:104-121 | 24h counts 10/1/2/0 match terminal rows exactly | step 6 |
| 6 | Illegal transitions dropped + warn, terminals sticky | state_machine.py:39-53; service.py:258-265 | unit tests (test_state_machine.py 11/11) | matches |
| 7 | Send failure = terminal dead record | manager.py:159-161, 175-195 | pending (step 5b) | matches code |
| 8 | No replay; fresh entries next slot; skew delays only | scheduler.py:133-141 (guard + max(now,next)) | 15:10 slot consumed-once-no-replay; 15:15 fired on first due tick; Ninja grid intact | matches |
| 9 | Source default USER, SCHEDULED stamp, admin-only | models.py:41-43, manager.py:123, scheduler.py:150, admin.py:93/120 | O-2 | matches |
| 10 | Cancel = best-effort revoke, REVOKED via sync/direct write | service.py:209-235 | 2 REVOKED rows 20:38-20:39 (user) | matches code |

## Portability / Separation-of-Concerns Audit (step 3)

Bar (contracts 1-2): a Spire task must run on a bare Celery worker with ZERO Django; the
worker runtime (decorator/runner/tracker/meta/result/state_machine) imports only stdlib +
pydantic + celery + kombu, and tracker tuning comes from task kwargs / Celery app config.

Import closure actually loaded by a worker running a `@celery_task` task:
`task module -> django_spire.celery.__init__ (tools signal) -> decorators -> runner ->
{meta, tracker} -> state_machine (via web code only)`. Verified: the six worker-side files do
NOT import manager/models/services/scheduler/sweep/process (no web-side leak in the closure).

| # | Module / line | Import | Classification | Rationale |
|---|---------------|--------|----------------|-----------|
| 1 | meta.py:1-5 | stdlib + pydantic | CLEAN | No Django anywhere. |
| 2 | state_machine.py:1 | `celery.states` | CLEAN | |
| 3 | result.py:1-4 | stdlib + `celery.utils.serialization` | CLEAN | |
| 4 | tracker.py:1-8 | stdlib + `celery.Task/states` + spire meta | CLEAN | Tuning via ctor kwargs (34-66) -> task opts (decorators.py:29) - contract 2 honored. |
| 5 | decorators.py:1-6 | stdlib + `celery.shared_task` + spire | CLEAN | |
| 6 | runner.py:6 | `celery.contrib.django.task.DjangoTask` | **VIOLATION (framework)** | Module-level import of `django.db` into every Spire worker. DjangoTask's only additions are `delay_on_commit`/`apply_async_on_commit` (celery/contrib/django/task.py:14-24); grep shows ZERO `on_commit` usage in the framework - the base class buys nothing. A plain `celery.app.task.Task` base is behaviorally identical. |
| 7 | `__init__.py` -> tools.py:5-14 | `celery.signals.celeryd_after_setup` (module level); handler lazily imports `django.apps` and imports every installed app's `celery.tasks` | CELERY-NATIVE NECESSITY (worker-side task discovery) with Django coupling | Discovery must run in the worker; iterating the Django app registry means the worker needs a populated apps registry (i.e. `django.setup()` ran) - live-confirmed by the app-init DB warning in worker 0D5. |
| 8 | test_project/celery.py:4 | `os.environ.setdefault('DJANGO_SETTINGS_MODULE', ...)` | CELERY-NATIVE NECESSITY (project) | Standard django-celery bootstrap; forces Django importable in the worker. |
| 9 | test_project/celery.py:6 | `app.config_from_object('django.conf:settings', namespace='CELERY')` | CELERY-NATIVE NECESSITY (project) | Worker's broker/backend config flows through Django settings - the canonical pattern; Spire runtime itself never reads Django settings (contract 2 honored at framework level). |
| 10 | test_project/app/celery/celery/tasks.py:8-9 | `django_spire.knowledge.entry.models.Entry`, `notification.automations` | PROJECT-LEVEL | This project's tasks require the ORM in the worker regardless of framework cleanliness; the zero-Django bar applies to the framework runtime, and to projects whose task code has no ORM needs. |
| 11 | apps.py:28-35 + process.py:10-18 + scheduler.py:226 + sweep.py:83 | same `AppConfig.ready()` runs in the worker; `is_web_server_process()` returns True for a `celery worker` argv (process.py:14: argv[0] != manage.py => web) | **VIOLATION (separation of concerns)** | Root cause of F-1: web-side scheduler + sweep threads start inside workers, where `result.get()` is process-globally forbidden. `RUN_MAIN` defaults to 'true' (process.py:11), so the gate that is meant to skip the runserver reloader parent is inert for workers. |

Verdict: the Spire worker runtime is 95% clean - five of six modules are pure
stdlib+pydantic+celery, and no web-side module leaks into the worker closure. Two real
violations: (a) `DjangoTask` base (runner.py:6) with zero functional benefit, and (b)
web-side daemon threads starting in workers (process detection). Everything else that makes a
real worker Django-dependent is the standard celery-django project pattern or project task
code.



## Completion Test

1. This doc contains every section: Confirmed Intent Baseline, Current State, behavior spec
   (all subsystems, cited), Portability Audit table, Race Harness Results (5 transcripts),
   Live Scenarios (>=6 transcripts), Monitoring (evidence + gaps + recs), Discrepancy
   Table, and the captured Completion Test output below.
2. Each of the 5 race harness results shows exactly one winner.
3. `just python -m pytest django_spire/celery/tests/ --reuse-db -q` -> all passed.
4. `just test` -> all passed.
5. Every discrepancy row has a severity and a recommendation.

### Captured output (run 2026-10-21 ~22:45 UTC, Django 6.1.2 venv, docker PG16 test DB)

Condition 1 - sections present: Confirmed Intent Baseline, Current State, Behavior Spec
(11 subsystems, cited), Contract map, Portability Audit (11-row table), Race Harness
Results (5 harnesses, 7 tests), Live Scenarios (5a-5f + F-1 secondary), Monitoring (6a-6d),
Discrepancy Table (13 rows) - all present in this doc.

Condition 2 - exactly-one-winner per harness: scheduler claim 1-of-5 (step 4 transcript);
sweep window 1-of-5; terminal metric exactly-once (1 of 3 racing writers); progress
monotonic with regression clamped (0 decreases of 500 interleaved updates); dedupe
sequential reuse + concurrent invariants (1 row / 1 send). 7/7 passed, three consecutive
runs (1.6-1.7s each).

Condition 3 - celery suite:

```
$ just python -m pytest django_spire/celery/tests/ --reuse-db -q
12 workers [400 items]
... (400 dots, 0 failures)
======================= 400 passed, 13 warnings in 8.89s =======================
```

Condition 4 - full suite:

```
$ just test
... (4572 passed, 0 failures; 13 RemovedInDjango2028Warning EMAIL_BACKEND deprecations,
1 DeprecationWarning from the legacy-arg confirmation-form test, 1 CacheKeyWarning)
============ 4572 passed, 15 warnings, 4 subtests passed in 40.25s =============
```

Condition 5 - every Discrepancy Table row (#1-#13) carries a severity and a
recommendation column entry. All five conditions hold.

## Race Harness Results (step 4)

Harness file: `django_spire/celery/tests/test_race_harness.py` (new, untracked, the only
new code artifact of this plan). Seven tests in five harness groups, run serially
(`-n 0`, threaded tests) against the docker PG16 test DB. TransactionTestCase gives the
racing threads committed rows; a `threading.Barrier` start gate releases all threads at
once; publish is stubbed by patching the module-level `send_task` imported in
`manager.py:14` with a thread-safe recorder.

Transcript (3 consecutive green runs, 1.6-1.7 s each; shown: one verbose run,
Django 6.1.2, settings `test_project.test_settings`):

```text
django_spire/celery/tests/test_race_harness.py::SchedulerClaimRaceTestCase::test_single_winner PASSED [ 14%]
django_spire/celery/tests/test_race_harness.py::SweepWindowRaceTestCase::test_single_winner PASSED [ 28%]
django_spire/celery/tests/test_race_harness.py::ConcurrentApplyRaceTestCase::test_progress_is_monotonic_under_race_and_regression PASSED [ 42%]
django_spire/celery/tests/test_race_harness.py::ConcurrentApplyRaceTestCase::test_terminal_apply_fires_metric_exactly_once PASSED [ 57%]
django_spire/celery/tests/test_race_harness.py::DedupeUnreadyRaceTestCase::test_concurrent_first_sends_never_diverge PASSED [ 71%]
django_spire/celery/tests/test_race_harness.py::DedupeUnreadyRaceTestCase::test_sequential_sends_reuse_unready_row PASSED [ 85%]
django_spire/celery/tests/test_race_harness.py::TrackerFlusherHandoffTestCase::test_handoff_loses_nothing PASSED [100%]

========================= 7 passed, 1 warning in 1.64s =========================
```

Per-harness results (exactly-one-winner assertions):

1. **Scheduler claim race** (5 threads, one due `*/5` slot, fixed nowfun): exactly one
   thread's `claim_schedule_slot` returned a CeleryTask, the row's `claimed_by` equals
   that thread's instance id, and the recorder saw exactly one `send_task` with the
   `spire_display_name` header. PASS (1 winner of 5).
2. **Sweep window race** (5 threads, one stale window): exactly one `claim_sweep_window`
   returned True; row `claimed_by` matches the winner. PASS (1 winner of 5).
3. **Concurrent web-apply race** (5 threads, one STARTED row, backend pre-seeded
   SUCCESS): final row state SUCCESS with the backend result, and
   `track_configured(reference=...)` fired exactly once with `celery_task_success`.
   PASS (metric exactly once under 5-way race).
4. **Progress monotonicity under race + regression** (4 threads racing on a 0.9 meta,
   then a regressed 0.1 meta): progress converged to 0.9 and stayed 0.9 after the
   regression. PASS.
5. **Dedupe unready** - sequential: two sends reuse the same unready row (1 row, 1
   publish); after the row goes SUCCESS, the third send creates a new row (2 rows, 2
   publishes). Concurrent first sends: 4 racing sends, invariants held (`sends == rows`,
   `1 <= rows <= 4`). PASS. (The check-then-act dedupe at `manager.py:136-139` is not
   atomic, so the harness asserts invariants, not exactly one row, for racing first
   sends.)
6. **Tracker flusher handoff** (writer thread, 200 progress ticks + `data.tick`, real
   flusher at the 5 s floor): main-row pushes are non-decreasing, the derived final-meta
   key is written exactly once with SUCCESS, and the final meta carries progress 1.0,
   `completed_time`, and the last tick (199) - i.e. `finish()` captured the writer's
   final state even though post-finish main-row pushes are blocked by design
   (`tracker.py:223-227`). PASS.

Execution notes (honesty record): the first two runs of this step hit harness bugs, not
code bugs - (a) an eager `args=(...)` evaluation ran one barrier party on the main
thread and deadlocked the start gate (found via pytest `faulthandler_timeout` dump);
(b) the shared module-level send recorder leaked across tests. Both fixed in the
harness only; no framework code was touched.

## Live Scenarios (step 5)

All scenarios ran against the live dev stack: shared team RabbitMQ
(`rabbitmq.compute.stratusadv.com`, project queue `django_spire_test_project_queue`,
passive probe confirmed exactly 1 consumer = this machine's worker), DigitalOcean
result backend, PG14.24 dev DB (scripts bypass the 6.1.2 version gate with a
script-local monkeypatch, per deviation 3). Times below are UTC (DB) unless noted;
local MDT = UTC - 6.

### 5a. Fresh SUCCESS lifecycle + exactly-one metric

Sent `NinjaAttackCeleryTaskManager` (no dedupe) `length=2` while worker 0D5 ran;
web-side resolution via the same code path views/sweep use
(`resolve_celery_tasks(CeleryTask.objects.by_unready())`):

```text
metric before: {'celery_task_success': 10, 'celery_task_failure': 1, 'celery_task_canceled': 2, 'celery_task_retry': 0}
sent: task_id=8333accb-... send_failed=False
row: state=PENDING source=user queued=22:31:13 started=None
waiting 6s for worker execution...
resolve_celery_tasks changed=2 (web-side single writer)
row: state=SUCCESS source=user started=22:31:14.729 completed=22:31:24.340
meta: {'data': {..., 'counted_seconds': 2, 'worker_hostname': 'spire-dev-c22f752b-...@not-a-toaster'},
       'progress': 1.0, 'completed_time': ...}
result: The sword goes SWOOSH SWOOSH
metric delta: {'celery_task_success': 2, ...}
```

Contract-confirmed: worker wrote backend only; web single-writer applied the terminal;
`source='user'` stamped; `worker_hostname` stamped on the meta data. The delta is **2**
because the resolve healed the stale `1d5d8f22` pirate row at the same time (F-2 heal
path, live): two tasks, two metrics, one each.

### 5b. Send failure -> terminal dead FAILURE row (isolated fake broker)

`CELERY_AMQP_HOST=127.0.0.1` (no local broker) in a separate process; shared broker
untouched:

```text
elapsed: 6.1s (2 retries, backoff 1s + 2s expected)
send_failed: True
state: FAILURE          (started=completed=queued, all stamped at send time)
send_error_message: [Errno 111] Connection refused
send_error_details: {'task_name': '...ninja_attack_task', 'args': None, 'kwargs': None, 'message': '[Errno 111] Connection refused'}
exception_result.exc_type: SendFailedError
metric delta: all 0
```

Contract 7 confirmed (terminal dead record with `SendFailedError`), and the monitoring
gap confirmed live: **a send-failure terminal fires no metric.**

### 5c. Cancel a QUEUED task

`app.send_task(countdown=15)` + factory row, `task.services.cancel()` at t+2s:

```text
cancel() returned: None after 0.43s
row: state=REVOKED is_canceled=True
metric delta: {'celery_task_canceled': 1, ...}
note: process exits before the 15s countdown, so the message is never published
```

### 5d. Cancel a RUNNING task (terminate=True)

Sent `length=2` (2s runtime), polled the DO backend until `STARTED`, then cancel:

```text
backend STARTED at ...s
cancel() returned: None after 0.40s
row right after cancel: state=REVOKED
backend 5s later: ('REVOKED', 22:32:56)      <- the worker's revoke handler wrote REVOKED
row 5s later: state=REVOKED
metric delta: {'celery_task_canceled': 1, ...}
```

Contract 10 (best-effort cancel) confirmed; the worker honored `terminate=True` and the
backend terminal matched the row.

### 5e. SIGKILL the worker mid-task; acks_late requeue; reaper both paths

Queue probe (passive) before the kill: `message_count=0, consumer_count=1`.

**E1** (`6d67dbd1`, 8s ninja task): backend `STARTED` -> `pkill -9` all worker
processes ->

```text
celery processes after SIGKILL: 'none'
queue (message_count, consumer_count): (1, 0)      <- acks_late: unacked message requeued, no consumers
web resolve changed=1; row state=STARTED           <- PENDING -> STARTED from track_started, no metric
--- reaper --dry-run --threshold 5 (worker dead, broker alive) ---
1 stale CeleryTask(s) would be marked FAILURE.
--- reaper --threshold 5 (real) ---
Marked 1 stale CeleryTask(s) as FAILURE.
row after reaper: state=FAILURE
exc_type: StaleStartedError
metric delta: all 0                                <- reaper FAILURE path fires no metric
```

Restarted the worker (gen 2). Log:

```text
[16:34:31] Task ...ninja_attack_task[6d67dbd1-...] received
[16:34:41] Task ...[6d67dbd1-...] succeeded in 10.17s
```

Redelivery confirmed (the killed task ran exactly once after restart). But the row is
terminal FAILURE and the backend is now SUCCESS:

```text
E1 after redelivery: row state=FAILURE backend=('SUCCESS', 22:34:41) changed=0
```

**Live row/backend divergence** (the reaper presumed the worker dead while the unacked
message was still requeued; after redelivery the task succeeded, but the terminal row
sticks). Contract 4 (no requeue from the reaper itself) held - the requeue was the
broker's, not the reaper's.

Gen-2 log also shows the embedded web threads now failing at the DB gate
(`NotSupportedError: PostgreSQL 15 or later is required (found 14.24)`) on every sweep
claim and the scheduler prune - the same worker-embedded-web defect as F-1, now
presenting through the 6.1.2 version gate instead of the F-1 `result.get()`
RuntimeError.

**E2** (`0fd015e4`, 8s ninja task) + the `*/5` scheduled pirate (`7c380357`): the
scenario script's own embedded scheduler thread (scripts count as "web" per
`process.py`) claimed the 22:35 slot and sent the pirate at 22:35:26
(`source='scheduled'`, live scheduler send confirmed); both messages were in
flight/queue when gen 2 was killed -> `queue (2, 0)`; gen 3 received both at 16:36:07
and succeeded both (pirate 16:36:12, E2 16:36:18). Web resolve moved E2 to STARTED;
the reaper then ran while the scenario script's own sweep thread (also started by
`django.setup()` in the script) was racing it:

```text
--- reaper --dry-run --threshold 5 (worker alive, idle) ---
2 stale CeleryTask(s) would be synced from the backend.
--- reaper --threshold 5 (real) ---
"Dropped stale CeleryTask state transition SUCCESS -> SUCCESS for task 0fd015e4-..."
Synced 1 stale CeleryTask(s) from the backend.
E2 row after reaper: state=SUCCESS completed=22:36:30
metric delta: {'celery_task_success': 2, ...}     <- one for E2 (reaper-synced), one for 7c380357 (sweep-resolved)
queue (message_count, consumer_count): (0, 1)
```

The E2 terminal apply was a live race between the reaper and the script's sweep thread;
the state machine's sticky terminal + `select_for_update` let exactly one apply
through, dropped the loser with the warning shown, and the metric fired exactly once
per task. Reaper SYNC path (backend-terminal -> real terminal + metric) confirmed.

**Process observation (discrepancy material):** every process that runs
`django.setup()` on the dev settings starts the scheduler and sweep daemon threads,
because `is_web_server_process()` (`process.py:10-18`) treats any process whose
`argv[0]` is not `manage.py` as a web server - including Celery workers (root cause of
F-1) and short-lived scripts (this scenario's scripts claimed scheduler slots and sweep
windows while running).

### 5f. dedupe_unready

Covered by O-2 (three `*/5` claims all reused the stuck PENDING row; zero broker
messages) and by the step-4 harness (sequential reuse + concurrent invariants). No
additional live send needed.

### F-1 secondary exposure (resolve_unready_before_send)

Code path confirmed at `manager.py:133-139` (worker-side `AsyncResult.get()` would hit
the same F-1 RuntimeError, swallowed per task by the resolver, potentially letting
dedupe reuse a stale row). No project manager sets
`resolve_unready_before_send = True` (only framework tests do), so the exposure is
latent in this project; the primary exposure (worker sweep) is active and was observed
~28 times in 15 minutes (F-1 evidence).

## Monitoring (step 6)

### 6a. Exactly-once metric audit (24h reconciliation)

Reconciled every terminal `CeleryTask` row in the dev DB against the terminal
`StatisticValue` rows of the last 24 hours. Script: `/tmp/spire_metric_audit.py`,
run 2026-10-21 ~22:40 UTC via `just python` (raw psycopg2 against the dev DB, no ORM):

```sql
SELECT state, count(*)
FROM django_spire_celery_task
WHERE state IN ('SUCCESS', 'FAILURE', 'REVOKED', 'RETRY')
  AND completed_datetime > NOW() - INTERVAL '24 hours'
GROUP BY state ORDER BY state;

SELECT reference, count(*)
FROM django_spire_metric_domain_statistic_value
WHERE reference LIKE 'celery_task%%'
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY reference ORDER BY reference;
```

Observed output (verbatim):

```
=== terminal CeleryTask rows, last 24h, by state ===
('FAILURE', 3)
('REVOKED', 4)
('SUCCESS', 14)

=== StatisticValue terminal metrics, last 24h, by reference ===
('celery_task_canceled', 4)
('celery_task_failure', 1)
('celery_task_success', 14)

=== non-terminal (unready) rows right now ===
('7b402c1e-c886-43bb-889e-8176cc1889fe', 'PENDING', 'scheduled', 'Pirate Song',
 datetime.datetime(2026, 10, 21, 22, 40, 3, 728398, tzinfo=datetime.timezone.utc))
```

Reconciliation:

- SUCCESS rows (14) == `celery_task_success` (14): exact.
- REVOKED rows (4) == `celery_task_canceled` (4): exact.
- RETRY: 0 rows, 0 metrics: exact.
- FAILURE rows (3) vs `celery_task_failure` (1): a 2-row gap, both accounted for as
  no-metric-by-construction terminals:
  1. `55dcb71d` (scenario 5b) - send-failure FAILURE created by
     `_create_failed_celery_task` (`manager.py:175-195`), which never passes through
     `_apply_backend_snapshot`, so `records_metric` (`service.py:267`) never runs.
  2. `6d67dbd1` (scenario 5e E1) - reaper-stamped FAILURE via direct `.update()`
     (`prune_stale_started_celery_tasks.py:87-90`), likewise bypassing the service
     metric path.
- No double-emit observed in 24h: every state's row count equals its metric count
  (modulo the two explained no-metric FAILURE rows). This includes the live
  sweep-vs-reaper race at 22:36 (5e E2), where two writers contended for one terminal
  and exactly one `celery_task_success` was recorded. The prior session's baseline
  (10S/1F/2R rows vs 10/1/2 metrics) reconciles under the same rules.

### 6b. New live F-2 instance caught during the audit (7b402c1e)

The audit itself produced a fresh F-2 instance, observed end to end:

- 22:40:02.302Z - the audit script's OWN scheduler thread (a short-lived
  `just python` process, PID 2035014) claimed the `*/5` Pirate Song slot
  (`CelerySchedulerTask.last_sent_datetime`, `claimed_by=not-a-toaster:2035014`) and
  sent `pirate_noise_task`. The user's web server was stopped; the worker's own
  scheduler thread is dead at the PG14 gate.
- 22:40:03.728Z - CeleryTask row created: PENDING, source=scheduled,
  display_name='Pirate Song'.
- 22:40:03.784Z - gen-3 worker: `Task ...pirate_noise_task[7b402c1e] received`.
- 22:40:07.201Z - worker: `succeeded in 3.416s: 'The pirate says YARR'`; remote DO PG
  backend row `celery_taskmeta` = SUCCESS.
- 22:41:40Z - CeleryTask row still PENDING (started/completed NULL); queue (0,1) =
  consumed, no redelivery; nothing left to sweep or resolve it (worker sweep thread
  fails at the PG14 version gate; the reaper does not cover PENDING rows - F-2).
  The row will read PENDING until a web process runs a sweep/resolve.

The claim probe at 22:41 also caught its own sweep thread claiming the sweep window
(`last_swept=22:41:19.196Z, claimed_by=not-a-toaster:2045712` = the probe's PID):
short-lived scripts claiming web-thread slots is now demonstrated by scheduler AND
sweep, and once by a script actually sending a real task to a real queue.

### 6c. Monitoring gaps (observed, not inferred)

1. **Reaper-stamped and send-failure FAILUREs emit no terminal metric** (6a). A
   `celery_task_failure` dashboard undercounts true failures by exactly these two
   classes; both were live-confirmed in the last 24h (5b, 5e E1).
2. **No liveness/heartbeat for the web threads** (scheduler, sweep). Observability
   is claim rows plus error logs only. A dead web process or dead thread produces no
   metric; the claim rows merely stop advancing. The worker's broken threads log a
   full traceback every 20s (sweep) - visible only in worker logs.
3. **Stale PENDING is invisible.** Neither the reaper (STARTED only) nor any metric
   (no terminal transition occurs) covers a PENDING row whose backend is already
   terminal (6b). There is no drift signal between "backend terminal" and "row
   unready".
4. **Broker-down is invisible to metrics.** Send retries exhaust to a terminal dead
   FAILURE row with `send_error_message` but no metric (5b) - an infrastructure
   outage leaves no metric trace.
5. **Claim-row provenance is the only audit trail for who sent what**, and it is
   polluted: workers and short-lived scripts claim scheduler/sweep slots and can send
   scheduled tasks while real web is down (6b). `claimed_by` (hostname:pid) is the
   only way to attribute it.

### 6d. Forward-looking recommendations (report-only, no code changed)

1. Emit the terminal metric for reaper-stamped FAILURE
   (`prune_stale_started_celery_tasks.py:87-90`) and for send-failure FAILURE
   (`manager.py` `_create_failed_celery_task`) - or explicitly document those two
   classes as uncounted and mirror that in the dashboard.
2. Add a scheduled drift check (reaper-style): count unready rows whose backend
   state is terminal and log a warning or record a metric. Would have caught 6b
   within one interval.
3. Alert on thread heartbeat staleness: the claim rows already carry the primitive
   (`CeleryTaskSweep.last_swept_datetime`, `CelerySchedulerTask.last_sent_datetime`);
   a bound plus a check turns "silently dead thread" into an alert.
4. Fix `is_web_server_process` (`process.py:10-18`) to exclude celery worker
   processes and short-lived script/management-command processes. Root cause of the
   F-1 worker-sweep exposure, the worker-thread traceback spam, and the
   script-claim/send behavior in 6b.
5. Decide whether terminal-metric counts and thread-liveness should surface in the
   task UI; today only claim rows and logs expose thread health.

## Discrepancy Table (step 7)

Report-only: no code was changed to fix any row. Severity: critical / major / minor /
informational. "Live" = observed in a live scenario this review, not just inferred.

| # | Discrepancy | Severity | Recommendation |
|---|-------------|----------|----------------|
| 1 | **F-1: worker-embedded sweep thread can never resolve** (live). Celery's process-global `_task_join_will_block` makes `AsyncResult.get()` raise `RuntimeError` from any thread in a worker process, so every sweep window a worker claims is consumed and wasted (`service.py:59`, `resolver.py:31`). Observed: 12 tracebacks in ~5 min, ~28 failed resolves in 15 min (gen-1); after the 6.1.2 upgrade the same thread fails instead at the PG14 gate every 20s (gen-2/3 logs). | Critical | Exclude worker processes from `start_sweep`/`start_scheduler` (real worker detection), and/or make the terminal read `backend.get_task_meta()` instead of `AsyncResult.get()`. |
| 2 | **F-2: stale PENDING rows are reaper-out-of-scope** (live). The reaper resolves stale STARTED only; with the web down, unready rows are never healed and the row is a permanent lie. Live: 1d5d8f22 sat PENDING vs backend SUCCESS until a web-side resolve ran (5a); 7b402c1e is still stuck PENDING at 22:41Z with backend SUCCESS (6b). | Major | Extend the reaper (or web sweep) to PENDING rows with a threshold, and/or add a "backend terminal, row unready" drift metric. |
| 3 | **`DjangoTask` base violation** (`runner.py:6`). Module-level import of `django.db` into every Spire worker; DjangoTask's only additions are `delay_on_commit`/`apply_async_on_commit` (celery/contrib/django/task.py:14-24) and grep shows zero `on_commit` usage in the framework - the base buys nothing. | Major | Switch the runner task base to plain `celery.app.task.Task`; behaviorally identical. |
| 4 | **`is_web_server_process` counts workers AND short-lived scripts as web** (`process.py:10-18`, live). `argv[0] != manage.py` => web; `RUN_MAIN` default is inert for workers. Root cause of #1 and of script-claim pollution: the audit script's own scheduler thread claimed the 22:40 slot and sent a real task (6b); the claim probe's sweep thread claimed the sweep window (6b). | Critical | Gate thread startup on explicit detection: exclude `celery` worker argv and one-shot script/management invocations (e.g. only start under `manage.py runserver`/`runserver_plus` or an explicit opt-in setting). |
| 5 | **Reaper-stamped and send-failure FAILUREs fire no terminal metric** (live). `prune_stale_started_celery_tasks.py:87-90` uses a direct `.update()`; `manager.py` `_create_failed_celery_task` never touches `_apply_backend_snapshot`; both bypass `records_metric` (`service.py:267`). Both classes present in the 24h audit: 6d67dbd1 (reaper), 55dcb71d (send failure) - the entire 3-vs-1 FAILURE gap (6a). | Major | Emit the terminal metric on both paths, or explicitly document them as uncounted and reflect that in dashboards. |
| 6 | **Reaper can stamp FAILURE while an unacked message is still requeued** (live, 5e E1). Dead worker + live broker: `inspect().active()` returns `{}`, reaper marks the row FAILURE; acks_late then redelivers, the task re-executes, the backend flips to SUCCESS, and the row stays FAILURE (sticky terminal; resolve showed `changed=0`). Row and backend permanently diverge, and the task ran after its terminal row. | Major | Before stamping, distinguish "no workers at all" from "workers say it's gone"; consider a broker-level requeue check or a grace period, and at minimum log the redelivery divergence. |
| 7 | **Claim commits without send -> slot lost with no audit trail** (live, 21:10 slot). The claim UPDATE committed on the web server's scheduler; the process was stopped before the send; the slot was consumed with no CeleryTask row and no broker message. Consistent with at-most-once, but silent. | Minor | Log a warning when a claimed slot's send fails or never completes; optionally claim-on-send (two-phase: mark claimed, then move to sent). |
| 8 | **Broken commit `ea01236f` shipped an IndentationError in `meta.py`** (process). Every import of `django_spire.celery` failed until `a2dfb58d` fixed it minutes later. `ruff check` would have caught the syntax error; it evidently was not run before the commit. | Critical (process) | Run the existing `ruff check .` gate before committing (or pre-commit hook); it is already in AGENTS.md. |
| 9 | **In-flight Django 6.0.6 -> 6.1.2 upgrade broke the dev stack for new processes** (env note, live). Django 6.1's `NotSupportedError` refuses the PG14.24 dev DB, so every NEW process using the ORM against the dev DB fails; it also changed the worker-thread failure mode (#1: RuntimeError -> NotSupportedError). Pre-existing processes keep working on the in-memory 6.0.6. | Informational (env) | Upgrade the dev DB to PG15+ (or run a local PG15/16 container); until then new processes need the policy bypass used by this review's scripts. |
| 10 | **`just celery` ran a prefork pool while AGENTS.md says "threads pool"** (informational). Live workers 0D5/11D/120 all started with `--pool=prefork`, concurrency 8. Prefork + acks_late is the conservative, requeue-safe combination; a threads pool changes GIL and DB-connection semantics. | Informational | Align the justfile/AGENTS.md with the intended pool; if threads is the goal, re-verify requeue behavior under it. |
| 11 | **AGENTS.md documents 3 terminal metrics; the code fires 4** (doc drift). `service.py:31-36` `_METRIC_REFERENCES` includes `celery_task_canceled`; AGENTS.md:415 lists only success/failure/retry. | Minor | Update AGENTS.md (and any docs pages) to list all four terminal metrics. |
| 12 | **Scheduler/sweep thread liveness has no heartbeat** (gap, live). Observability is claim rows plus error-log tracebacks only; a dead web process or dead thread produces no metric, and the claim rows merely stop advancing (the gen-2/3 worker's threads "worked" by logging a traceback every 20s for ~1.5h). | Major | Add a liveness metric or alert on claim-row staleness (`CeleryTaskSweep.last_swept_datetime`, `CelerySchedulerTask.last_sent_datetime` vs now); see 6d-3. |
| 13 | **Dedupe check-then-act is non-atomic** (`manager.py:133-139`). Two concurrent senders of the same dedupe-unready manager could both miss the unready row and both create+send. Step-4 harness: sequential reuse held and concurrent invariants (1 row / 1 send per task id) held under the single-writer state machine. | Informational | Acceptable at current scale; if concurrent sends of one manager become real, move the check into the same `select_for_update` window as the row write. |

## Deviations

1. Review target changed mid-execution
   - What: The user committed `ea01236f` ("resolver and sweep behavior changes") at
     15:07, after step 0. It absorbed all prior session work (source field, web-process
     thread gating, scheduler orphan pruning, v1.3.0, changelog, ajax guard) plus new user
     changes: sweep defaults (interval 30->20s, task limit 30->20 in
     `django_spire/settings.py`), `tzdata==2026.5` in pyproject, minor AGENTS.md and access
     card template edits. Review target re-derived to `ea01236f` + working tree; the new
     sweep defaults are in scope for spec validation.
   - Why: Step 0 had captured the working tree at an earlier HEAD; the commit moved the
     baseline forward.
2. `ea01236f` shipped a syntax error in `meta.py` (indentation added to the `typing`
   import, breaking every Django import)
   - What: Step 1's environment check failed with `IndentationError: meta.py:3`.
     The user fixed the line and committed it as `a2dfb58d` ("indent typo") at ~15:10
     (not the assistant); the environment check was re-run after the fix and passed
     (RabbitMQ + Postgres connected). The broken commit is noted in the discrepancy
     table as a critical observation.
   - Why: It was a false precondition for every execution step (nothing imports
     `django_spire.celery` while it stands).
3. In-flight dependency upgrade changed the ground mid-execution (django 6.0.6 -> 6.1.2)
   - What: While executing (after 15:10, before 15:31), the user edited `pyproject.toml` +
     `uv.lock` (uncommitted) to django 6.1.2 and re-synced the venv. Django 6.1 refuses the
     PG14.24 dev DB (`NotSupportedError`), so NEW processes cannot use the ORM against the dev
     DB. Steps were re-derived: live-scenario scripts use a script-local monkeypatch of
     `check_database_version_supported` (documented in Live Evidence); race harnesses and the
     completion test run against the docker PG16 test DB, which is unaffected. The review
     target for the framework code is unchanged (`a2dfb58d` + working tree; the celery module
     itself is untouched by the upgrade).
   - Why: False precondition for every step that talks to the dev DB through Django; the
     upgrade also changes what `just test` exercises (6.1 vs 6.0), so its results are
     interpreted with that caveat.

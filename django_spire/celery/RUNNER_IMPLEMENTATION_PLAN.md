# `CeleryTaskRunner` Implementation Plan

Status: FINAL v3 — reviewed against KISS/DRY/YAGNI; all decisions logged in §8
Location of code: `django_spire/celery/runner.py` (new), `tracker.py` (restructured), `state_machine.py` (new), plus the files listed per phase
Celery version assumed: 5.6.3 (verified against the installed source)

## 1. Purpose

`CeleryTaskRunner` is a base class for **the actual Celery task** (not the `CeleryTask`
shadow model). It gives a framework to extend and automate the logic in
`CeleryTaskMeta` and `CeleryTaskTracker`, with control over updating and
race conditions.

**Division of labor (two components, both per-execution):**

| | `CeleryTaskRunner` (extends `celery.Task`) | `CeleryTaskTracker` |
|---|---|---|
| Job | **Runs**: claim the row, create the per-execution tracker, exception/retry/abort handling, terminal orchestration | **Tracks**: owns `CeleryTaskMeta`, state + progress accumulation, the single-writer flusher, and every atomic row write |
| Lifecycle | Per execution (thread-local on the shared task instance) | Per execution; created by the runner **with the claimed row** passed in |
| Task-author API | `self.tracker`; extend by overriding `on_success`/`on_failure`/`on_retry` or connecting `task_*` signals (native Celery) | Unchanged surface: `set_started`, `set_completed`, `set_started_and_completing_soon`, `update_state`, `update_count_progress`, `update_cumulative_progress`, `set_cumulative_progress_target_value`, `meta` (+ new `set_data`, `set_retries`) |

End state: the worker (runner + tracker) is the single writer of the `CeleryTask` row;
the web UI polls a plain SELECT (polling architecture unchanged — reads only get
cheaper); the Celery result backend (`db+postgresql`, separate `celery-development`
database) is kept but demoted to a best-effort compatibility mirror so `AsyncResult`,
chords, and the demo's direct `AsyncResult(...).get()` keep working.

## 2. Current state (verified facts)

### 2.1 Flow today

```
WEB process                      WORKER                        WEB process (UI poll)
─────────────                    ────────                      ─────────────────────
Manager.send_task()
  → celery send_task()   ───►    shared_task runs
  → CeleryTask row created        CeleryTaskTracker pushes
    (AFTER the send, PENDING)     state+meta to the result
                                   backend (db+pg, separate DB)
                                            ◄────  Glue.view re-render every 2–4s (jitter)
                                            _task_view →
                                            service.update_from_async_result_and_save_if_change()
                                            (reads backend, WRITES row,
                                             lazy result capture in .result property)
```

### 2.2 Celery 5.6.3 mechanics that constrain the design

| Fact | Source (installed package) | Design consequence |
|------|----------------------------|--------------------|
| Tracer calls `task.run` directly unless `__call__` is overridden | `celery/app/trace.py:377` | Hook `run()`, don't override `__call__` |
| With `task_track_started=True` (set in `test_project/celery.py`) the tracer itself writes `store_result(id, {'pid','hostname'}, STARTED)` before `run()` | `trace.py:574-578` | Harmless with the new design (backend is a mirror); row STARTED is written by our claim |
| Success path order: `mark_as_done` → `on_success` → `task_success` → `after_return`; failure: `mark_as_failure` → `on_failure`; `Retry` → `mark_as_retry` → `on_retry`; `task_postrun` in `finally`; `on_success`/`on_failure`/`on_retry` are called by the tracer when overridden | `trace.py:475-663` | Terminal row write happens inside `run()` (before `mark_as_done`); native `on_*` overrides + `task_*` signals are the extension points |
| `db+` backend: `_store_result`/`_update_result` set EVERY column from each write, nulling absent ones; no merge, no versioning, last-write-wins | `celery/backends/database/__init__.py:150-184` | Backend is a dumb mirror; never the source of truth |
| `acks_late=True` + `task_reject_on_worker_lost=True` (both set) → a dead worker's in-flight task is REDELIVERED and executed a second time with the same `task_id` | `test_project/celery.py`; `worker/request.py:341-372` | Need a row claim/lease; Celery's `worker_deduplicate_successful_tasks` (off) only covers already-SUCCESS redeliveries |
| Threads pool: one registered task instance shared across worker threads; `task.request` is safe only because `request_stack = LocalStack()` (thread-local) | `app/task.py:381`, `utils/threads.py:305` | The per-execution tracker must live in a `threading.local` slot, not an instance attribute |
| Django fixup (auto-installed, `DJANGO_SETTINGS_MODULE` set): `django.setup()` before task import; **DB connection closed on `task_prerun` AND `task_postrun`** | `celery/fixups/django.py:191-199` | All DB work must finish inside `run()`; the flusher may not outlive the task; final flush is synchronous on the task thread |
| Default task base is `celery.contrib.django.task.DjangoTask` (adds `delay_on_commit`); custom `apply_async(headers=...)` land on `self.request` in the worker | `fixups/django.py:82-86`; `app/amqp.py:510-511`; `worker/request.py:98` | Runner subclasses `DjangoTask`; reference/model keys travel in message headers |
| `celery.utils.ext ExceptionInfo` provides `pickle()`/`restore()` — Celery's own failure serialization, used by the backends | `celery/utils/ext.py` (via `app/trace.py` `handle_failure`) | Reuse for `CeleryExceptionResult` (§4.7) |
| `apply_async(headers=...)` merges into AMQP message headers → `Request._request_dict = message.headers.copy()` | `app/amqp.py:509-511`; `worker/request.py:98` | Manager→worker key passing mechanism |

Note: `celery.states.state` precedence comparison (SUCCESS/FAILURE > REVOKED > STARTED
> ... > PENDING) was considered for state guarding and **rejected**: it rejects the
legitimate `STARTED → RETRY` transition (RETRY ranks below STARTED). An explicit
transition table is both correct and simpler (§4.1).

### 2.3 Race-condition & bug catalog

| # | Where | Problem |
|---|-------|---------|
| R1 | `tracker.py:10` | Module-level `ThreadPoolExecutor(100)` shared by all tasks; only the newest `Future` is tracked → two in-flight writes from one task can land out of order (db backend last-write-wins) |
| R2 | `tracker.py:64-73` | `set_completed()` → sync `update_state` + `time.sleep(2)` hack racing the tracer's `mark_as_done`; row merge (`_merge_meta_into_celery_task`) commented out → final `meta.data` lost (the 4 currently-failing tests in `tests/test_tracker.py:87-145` describe this) |
| R3 | `service.py:25-48` + db backend | The backend `result` column receives either the tracker's meta dict or the task's return value depending on which write lands last → shadow-row `_result` can hold the meta dict instead of the return value |
| R4 | `manager.py:107-140` | Row created AFTER `send_task` returns; no claim/lease anywhere → worker can execute (or be redelivered) before/without the row |
| R5 | `service.py:50-89` | Web sync path is read-modify-write with no versioning; PENDING-regression guarded by one special case; item view + toast list poll concurrently → clobbering possible |
| R6 | `service.py:70-78` | `_apply_completed_meta` runs for FAILURE too (`ready()` is True) → `set_completed()` on failed tasks → failed tasks display 100% progress |
| R7 | `meta.py:117-119` | `set_started_and_completing_soon` sets `last_update_time = time.time() + 1` (future) → `estimated_progress` decreases |
| R8 | `meta.py` generally | Epoch timestamps written by the worker, extrapolated by the web across machines → clock skew in UI ETA/progress. **Assessment after review:** acceptable with NTP-synced hosts + the existing 10% ETA buffer; no schema change for this |
| R9 | `tracker.py:142-153` | `_cumulative_progress`/`_state` mutated without a lock; `update_count_progress(c, 0)` → ZeroDivisionError |
| R10 | `querysets.py:30-31` | `by_completed()` uses `state__in=states.SUCCESS` — `__in` with a string iterates characters (`IN ('S','U','C','E','S')`) → always empty → `queue_service.py:19-21` guaranteed ZeroDivisionError |
| R11 | `models.py:142-153` | `CeleryTask.result` property has write side effects (calls `update_result` → DB write) |
| R12 | `service.py:44-48` | `F('result_capture_attempts') + 1` set without a save in all paths |
| R13 | `meta.py:121-132` | `merge()` iterates only `model_fields` — `extra='allow'` fields dropped; `data` merged shallowly |
| R14 | `models.py:21` | `task_id` not unique → claim `get_or_create` unsafe |
| R15 | `models.py:102-104` | `is_processing` True for `REJECTED`/`IGNORED` (not in `READY_STATES` in this Celery version) |

## 3. Target architecture

```
WORKER (CeleryTaskRunner wraps the real celery.Task; owns a CeleryTaskTracker)
  run()
   ├─ claim row: get_or_create(task_id) + CAS PENDING→STARTED      ← runner
   ├─ tracker = CeleryTaskTracker(self, celery_task_model=row)     ← per execution, thread-local
   ├─ execute(*args, **kwargs)  — user code calls tracker.* as today
   │     tracker: meta + progress (locked) → coalescing mailbox
   │              → single-writer flusher thread (FIFO, in issue order)
   │              → DB row (transaction, state machine, monotonic progress)
   │              → backend mirror (best effort)
   ├─ success:  tracker.finish(SUCCESS, result)  — synchronous, ordered, on task thread
   ├─ failure:  tracker.finish(FAILURE, exc)     — stores CeleryExceptionResult, ordered
   ├─ retry:    tracker.finish(RETRY)            — synchronous, ordered
   └─ return    ← DjangoWorkerFixup closes the DB connection on task_postrun AFTER this
                 (tracer then runs on_success/on_failure — overridable, signals fire)

WEB:  _task_view → pure SELECT for runner rows (legacy rows keep the old sync path)
      (polling architecture unchanged — reads only get cheaper)
MANAGER: soft dedupe on send (per-manager opt-in) + keys passed in message headers
```

Key decisions:

1. `CeleryTaskRunner` subclasses `celery.contrib.django.task.DjangoTask` — the real
   Celery task. `self.request`, `self.retry()`, `self.backend`, `self.update_state`
   are native. User tasks keep function style via `@spire_task`
   (`shared_task(base=CeleryTaskRunner, bind=True)`), so existing
   `BaseCeleryTaskManager.task_name` strings keep working unchanged.
2. **Runner runs, tracker tracks.** The runner orchestrates the lifecycle and hands
   the claimed row to a per-execution `CeleryTaskTracker`. The tracker owns all
   meta/state/progress logic and every row write (the commented-out
   `_merge_meta_into_celery_task` finally becomes real, atomic).
3. Every row state change goes through an atomic write guarded by an **explicit
   state machine** (transitions table; custom states allowed from any non-terminal
   state; terminals sticky; never back to PENDING/RECEIVED). Only the worker writes,
   so there is no cross-process read-modify-write. No version column needed — the
   single-writer flusher + `select_for_update` + the machine are sufficient.
4. Terminal writes (success/failure/retry) are synchronous and ordered on the task
   thread — kills R2/R3, removes `time.sleep(2)`.
5. Per-tracker single-writer flusher (coalescing mailbox, FIFO apply) replaces the
   shared 100-worker executor — kills R1/R9.
6. Claim on start (unique `task_id` + CAS) handles the row-creation gap and acks_late
   redelivery — kills R4. **Redelivery policy: hard-coded abort** — a task whose row
   is already claimed by another worker raises `Reject(requeue=False)` (no config
   knob).
7. Send-time dedup is **per-manager opt-in and soft** (`dedupe_unready=True`): the
   manager reuses the existing unready row. No DB index; the residual
   simultaneous-send race is today's behavior and accepted.
8. Result backend stays as the best-effort mirror.
9. `meta.data` gets **typed per-task validation** (`data_model`, a pydantic model) —
   validated on `tracker.set_data(...)`.
10. Custom states stay **free-form in the row `state` column**; the state machine
    allows them from any non-terminal state.
11. Failure rows store a **`CeleryExceptionResult`** (sibling of `CeleryNoResult`) in
    `_result`, built from Celery's own `ExceptionInfo.pickle()` mechanism.
12. UI polling architecture stays as-is; runner rows just become pure DB reads.
13. **Extension is Celery-native**: override `on_success`/`on_failure`/`on_retry` on
    the runner (the tracer calls them) or connect `task_*` signals. No custom
    before_run/after_run hooks.
14. **Minimal schema**: only `task_id unique` + `runner_managed` boolean. Worker
    hostname and retry count live in the meta dict; no `meta_version`,
    `last_update_datetime`, `worker_hostname`, or `retries` columns.

## 4. Design

### 4.1 State machine — new `django_spire/celery/state_machine.py`

```python
from celery import states


class CeleryTaskStateMachine:
    BASE = {
        states.PENDING:   {states.STARTED, states.FAILURE, states.REVOKED, states.REJECTED},
        states.RECEIVED:  {states.STARTED, states.FAILURE, states.REVOKED, states.REJECTED},
        states.STARTED:   {states.SUCCESS, states.FAILURE, states.RETRY, states.REVOKED},
        states.RETRY:     {states.STARTED, states.FAILURE, states.REVOKED},
        states.SUCCESS:   set(),   # terminal, sticky
        states.FAILURE:   set(),
        states.REVOKED:   set(),
        states.REJECTED:  set(),
    }

    @staticmethod
    def _anchor(state: str) -> str:
        # custom/progress states ('MAKING NOISES') anchor to STARTED
        if state in states.READY_STATES or state in (
            states.PENDING, states.RECEIVED, states.RETRY, states.REVOKED, states.REJECTED,
        ):
            return state
        return states.STARTED

    @classmethod
    def ok(cls, current: str, to: str) -> bool:
        if to in states.READY_STATES:
            return current not in states.READY_STATES   # terminals are sticky
        if to in (states.PENDING, states.RECEIVED):
            return False                                # never regress to "queued"
        if to not in states.ALL_STATES:
            return True                                 # custom state: any non-terminal
        return to in cls.BASE[cls._anchor(current)]
```

Correctness notes (reviewed):

- `STARTED → RETRY` allowed (the precedence-based check rejected this — why it was dropped)
- custom → custom and STARTED → custom allowed; custom → plain `STARTED` rejected
  (labeling is monotonic); custom → terminal allowed
- double terminal write (duplicate `finish`) rejected → idempotent drop, logged

### 4.2 `CeleryTaskMeta` extensions — `django_spire/celery/meta.py` (extend, keep)

```python
class CeleryTaskMeta(BaseModel):
    # existing fields unchanged: data, progress, started_time, last_update_time,
    # estimated_completed_time, completed_time, _progress_updates_count
    retries: int = 0
    error: str | None = None          # one-line summary; full detail in
    failed_time: float | None = None  # CeleryExceptionResult on the row

    def set_failed(self, error: str) -> None:
        self.error = error
        self.failed_time = time.time()
        # deliberately does NOT touch progress or completed_time (fixes R6)

    def set_started_and_completing_soon(self):
        self.set_started()
        self.progress = 1.0
        self.estimated_completed_time = time.time() + 5
        self.last_update_time = time.time()          # R7 fix (was time.time() + 1)

    def merge(self, other: Self) -> Self:
        # R13 fix: iterate other.model_dump() so extra='allow' fields survive;
        # deep-merge `data` recursively
        ...
```

(Worker hostname is also written into `meta.data['worker_hostname']` at claim time —
debug info, no column needed.)

### 4.3 Runner — new `django_spire/celery/runner.py` (orchestration only)

```python
class CeleryTaskRunner(DjangoTask):
    # ---- per-task config (class attr or decorator options) ----
    runner_display_name: str | None = None
    runner_update_interval_seconds: int = 5          # tracker enforces min 5
    data_model: type[BaseModel] | None = None

    # ---- per-execution state (thread-local: threads pool shares one instance) ----
    _local = threading.local()

    @property
    def tracker(self) -> CeleryTaskTracker | None:
        return getattr(self._local, 'tracker', None)

    # ================= TEMPLATE METHOD (tracer calls task.run directly) =================
    def run(self, *args, **kwargs):
        tracker = self._start_execution()
        try:
            result = self.execute(*args, **kwargs)   # user code; uses self.tracker
        except (Reject, Ignore):
            raise
        except Retry:
            tracker.set_retries(self.request.retries)
            tracker.finish(states.RETRY)
            raise
        except Exception as exc:
            tracker.finish(states.FAILURE, exc=exc)  # stores CeleryExceptionResult
            raise                                     # tracer still does mark_as_failure
        tracker.finish(states.SUCCESS, result=result)
        return result

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    # ================= LIFECYCLE =================
    def _start_execution(self) -> CeleryTaskTracker:
        if not self.request.id or self.request.called_directly:
            return CeleryTaskTracker(self)           # untracked mode (no row, no flusher)

        row, _ = CeleryTask.objects.get_or_create(   # R4: safe once task_id UNIQUE
            task_id=self.request.id,
            defaults=dict(task_name=self.name, display_name=...,
                          reference_key=self.request.get('spire_reference_key'),
                          model_key=self.request.get('spire_model_key'),
                          state=states.PENDING, queued_datetime=now(),
                          runner_managed=True),
        )
        claimed = CeleryTask.objects.filter(
            task_id=self.request.id,
            state__in=(states.PENDING, states.RECEIVED, states.RETRY),
        ).update(state=states.STARTED, started_datetime=now())
        if not claimed:
            raise Reject(requeue=False)              # decided: hard-coded abort

        tracker = CeleryTaskTracker(
            self,
            celery_task_model=row,                   # the stub finally becomes real
            update_interval_seconds=self.runner_update_interval_seconds,
            data_model=self.data_model,
        )
        tracker.set_started()                        # meta (incl. hostname) + sync write
        self._local.tracker = tracker
        return tracker
```

Extension points (no custom hooks): override `on_success(retval, task_id, args,
kwargs)` / `on_failure(exc, ...)` / `on_retry(...)` on a subclass (the tracer calls
them after `run()` returns/raises, DB still open until `task_postrun`), or connect
`task_success` / `task_failure` / `task_prerun` / `task_postrun` signals globally.
Class-based usage also works with zero extra code: subclass the runner, set `name`,
override `execute`, register the task.

### 4.4 Tracker — `django_spire/celery/tracker.py` (restructured, same public API)

```python
class CeleryTaskTracker:
    _FLUSH_TIMEOUT_SECONDS = 10                      # module constant

    def __init__(
        self,
        celery_task: Task,
        update_interval_seconds: int = 5,
        celery_task_model: CeleryTask | None = None,   # was a commented-out stub
        data_model: type[BaseModel] | None = None,     # new: typed meta.data
    ) -> None:
        # same min-5 validation as today
        self.meta = CeleryTaskMeta()
        self._celery_task = celery_task
        self._celery_task_model = celery_task_model    # the claimed row (single writer)
        self._data_model = data_model
        self._lock = threading.Lock()                  # R9: protects meta/progress/state
        self._mailbox_snapshot = None
        self._mailbox_event = threading.Event()
        self._flusher = None                           # started in set_started() when tracked

    # ---- unchanged public surface (task author API) ----
    @property
    def task(self) -> Task: ...
    def set_started(self) -> None: ...                 # also starts the flusher thread
    def set_completed(self) -> None: ...               # mid-run: becomes a scheduled
    def set_started_and_completing_soon(self) -> None: # update (progress=1, ETA), NOT
    def update_state(self, state: str = states.PENDING) -> None: ...   # the terminal write
    def update_count_progress(self, current_count, target_count,
                              range_min=0.0, range_max=1.0) -> None: ...   # R9 zero guard
    def set_cumulative_progress_target_value(self, value: int) -> None: ...
    def update_cumulative_progress(self, added_value: int) -> None: ...    # locked (R9)
    def set_data(self, **kwargs) -> None: ...          # new: merges + validates
    def set_retries(self, count: int) -> None: ...

    def _validate_data(self, data: dict) -> None:
        # no-op when data_model is None; else model_validate on the merged dict

    # ---- new: ordered, atomic, terminal (called by the runner, not task code) ----
    def finish(self, state: str, result: Any = None, exc: BaseException | None = None) -> None:
        if state == states.SUCCESS:
            self.meta.set_completed()
        elif state == states.FAILURE:
            self.meta.set_failed(f'{type(exc).__name__}: {exc}')
        snapshot = self._snapshot(state, result=result, exc=exc)
        if self._celery_task_model is None:
            return                                     # untracked mode
        if self._flusher is not None:
            self._stop_flusher()                       # join in-flight write (ordered)
        self._merge_meta_into_celery_task(snapshot)    # on the TASK thread

    # ---- internal: replaces force_update_celery_task_state / sleep(2) (R2) ----
    def _merge_meta_into_celery_task(self, snapshot) -> None:
        _apply_to_row(self._celery_task_model, snapshot)
        self._push_to_backend(snapshot)                # best-effort mirror, log on error
```

Flusher (lives inside `tracker.py`, ~30 lines, no separate file):

```python
    def _start_flusher(self) -> None:
        self._flusher = threading.Thread(target=self._flusher_loop, daemon=True)
        self._flusher.start()

    def _flusher_loop(self) -> None:
        while not self._stopped.is_set():
            self._mailbox_event.wait(timeout=self._update_interval_seconds)
            self._mailbox_event.clear()
            snapshot = self._take_mailbox_snapshot()   # latest only (coalescing)
            if snapshot is not None:
                self._merge_meta_into_celery_task(snapshot)

    def _stop_flusher(self) -> None:
        self._stopped.set()
        self._flusher.join(timeout=self._FLUSH_TIMEOUT_SECONDS)
```

The mailbox is a locked variable + `threading.Event` (latest snapshot wins), not a
separate class. What the tracker keeps: the constructor shape (the
`celery_task_model` stub becomes live), the public method names, the
`CeleryTaskMeta` ownership, the 5-second minimum interval rule. What changes:
executor → per-tracker flusher thread (R1); `sleep(2)` → ordered synchronous
`finish()` (R2); row merge implemented atomically (R2, R3); lock around
progress/state/meta (R9); zero-target guard (R9); `set_data` validation; all row
writes through `CeleryTaskStateMachine` + monotonic progress.

### 4.5 The atomic row write — module function in `tracker.py` (used by the tracker only)

```python
def _apply_to_row(row: CeleryTask, snap) -> None:
    with transaction.atomic():
        fresh = CeleryTask.objects.select_for_update().get(pk=row.pk)

        if not CeleryTaskStateMachine.ok(fresh.state, snap.state):
            log.warning('dropped stale transition %s -> %s', fresh.state, snap.state)
            return

        merged = fresh.meta.merge(CeleryTaskMeta(**snap.meta_dict))
        if merged.progress is not None and (fresh.meta.progress or 0) > merged.progress:
            merged.progress = fresh.meta.progress                      # monotonic

        if snap.state == states.SUCCESS:
            fresh._result = pickle.dumps(snap.result)                  # real value (R3)
            fresh.completed_datetime = now()
        elif snap.state == states.FAILURE:
            fresh._result = pickle.dumps(snap.exception_result)        # §4.6
            fresh.completed_datetime = now()

        fresh.state = snap.state
        fresh._task_meta = merged.model_dump()
        fresh.save()
        row._task_meta = fresh._task_meta

    # backend mirror AFTER the DB write (AsyncResult/chords compat) — best effort:
    # task.backend.store_result(task_id, snap.meta_dict, snap.state) in try/except
```

If `select_for_update` ever becomes a problem (SQLite), the swap is local to this
function: optimistic retry of the whole block (no version column required — the
state machine re-checks against `fresh` on each attempt).

### 4.6 `CeleryExceptionResult` — extend `django_spire/celery/result.py`

```python
class CeleryExceptionResult:
    """Stored in CeleryTask._result for FAILURE rows (sibling of CeleryNoResult).
    Built from celery.utils.ext.ExceptionInfo — the SAME mechanism Celery's own
    backends use to serialize failures (ExceptionInfo.pickle())."""

    def __init__(self, exc: BaseException, einfo_pickle: bytes | None,
                 traceback_text: str | None) -> None:
        self.exc_type = type(exc).__name__
        self.message = str(exc)
        self.traceback = traceback_text
        self._einfo_pickle = einfo_pickle      # None when the exception isn't picklable

    @property
    def exception(self) -> BaseException | None:
        # full restore only when picklable; same trust domain as the _result pickle
        ...

    def __str__(self) -> str:
        return f'{self.exc_type}: {self.message}'
```

- Built in `tracker.finish(FAILURE, exc=...)`: `einfo = ExceptionInfo()` captures
  `sys.exc_info()`; `einfo.pickle()` inside try/except (fall back to
  `traceback.format_exception` text only).
- Model additions: `CeleryTask.has_exception_result`, `CeleryTask.exception_result`;
  `CeleryTask.result` stays `None` for FAILURE rows (contract preserved);
  `has_result`/`has_no_result` semantics unchanged.
- Templates + admin show `exception_result.message` (admin readonly field,
  `task_content.html` failure block).
- Optional cleanup (separate commit): the legacy `{'error': 'SEND_FAILED', ...}`
  dict in `_create_failed_celery_task` can migrate to
  `CeleryExceptionResult(exc_type='SendFailedError', ...)`; `send_failed` property
  keeps working during the transition.

### 4.7 Decorator — `spire_task`, in `runner.py`

```python
def spire_task(data_model=None, display_name=None, update_interval_seconds=5, **task_opts):
    def decorate(fun):
        def run(self, *args, **kwargs):
            self._configure_run(data_model=data_model, display_name=display_name,
                                update_interval_seconds=update_interval_seconds)
            return self._run_lifecycle(fun, args, kwargs)
        run.__name__ = fun.__name__                    # -> same task_name as today
        run.__wrapped__ = fun
        return shared_task(base=CeleryTaskRunner, bind=True, **task_opts)(run)
    return decorate
```

Migrated task example (`test_project/app/celery/celery/tasks.py`) — the body shape is
almost unchanged from today:

```python
class PirateSongData(BaseModel):
    counted_seconds: int
    more: dict | None = None

@spire_task(display_name='Pirate Song', data_model=PirateSongData)
def pirate_song_task(self, length: int) -> str:
    tracker = self.tracker
    tracker.meta.data['bananas'] = 'The #&A$ is the key!'

    if length <= 5:
        tracker.set_started_and_completing_soon()
    else:
        tracker.set_started()
        tracker.set_cumulative_progress_target_value(length)

    for i in range(length):
        sleep(1)
        tracker.set_data(counted_seconds=i + 1)        # validated against PirateSongData
        if length > 5:
            tracker.update_cumulative_progress(added_value=1)
            tracker.update_state('MAKING NOISES')

    tracker.set_data(more={'has_noises': True})
    return 'The song sounds like' + ' YO HO' * length  # terminal finish() is the runner's job
```

Note: the manual `tracker.set_completed()` is removed from migrated bodies — the
runner's `finish(SUCCESS)` is the terminal write. A `set_completed()` called mid-run
behaves as a scheduled update (progress=1, completed_time set) but never terminates.

### 4.8 Manager changes — `django_spire/celery/manager.py`

- `dedupe_unready: bool = False` — **per-manager opt-in, soft**: `send_task` first
  looks up an unready row for `(reference_key, model_key)` and returns it if one
  exists. No DB index, no error path — the residual simultaneous-send race is
  today's behavior and accepted.
- Pass `headers={'spire_reference_key': ..., 'spire_model_key': ...,
  'spire_display_name': ...}` on send (lands on `self.request` in the worker), so the
  claim can create a complete row in the fallback gap case.
- Keep the existing retry/backoff loop and `_create_failed_celery_task` path.

### 4.9 Web side — `django_spire/celery/views/task_views.py`

```python
def _task_view(request, template, task_id):
    celery_task = get_object_or_404(CeleryTask, task_id=task_id)
    if not celery_task.runner_managed:
        celery_task.services.update_from_async_result_and_save_if_change()  # legacy
    ...
```

- `CeleryTask.result` becomes a pure read (side-effect capture moves to the tracker's
  terminal write). `CeleryTaskService` is otherwise unchanged (legacy path + phase-0
  fixes only — no write/read split).
- Polling architecture unchanged (decided): same `Glue.view` re-render loops; runner
  rows just make each poll a local-DB SELECT.
- Failure display: `task_content.html` shows `exception_result.message` for failed
  tasks (currently a static "Task Encountered an Error or Took to Long");
  `CeleryTaskAdmin` gains an `exception_result` readonly field.

### 4.10 Schema migration (one migration, two changes)

```
task_id:         unique=True                     (R14)
runner_managed:  BooleanField(default=False)     (gates the legacy web sync path)
```

No other columns: hostname + retry count live in meta; no `meta_version`,
`last_update_datetime`, `worker_hostname`, `retries`, or `dedupe_enabled`; no
partial unique index (soft dedup).

### 4.11 Settings

- `test_project/celery.py`: add `worker_deduplicate_successful_tasks=True` (verified:
  effective with `acks_late` + persistent backend — both true here) as a second
  redelivery guard (phase 4).
- `task_revoked` signal handling is phase-5 optional (see §5).

## 5. Phased delivery (all phases; phase 5 is pick-what-you-need)

### Phase 0 — bug fixes (no behavior change)

Files: `querysets.py`, `meta.py`, `services/service.py`, `services/queue_service.py`,
`models.py`.

- R10 `by_completed()` → `state__in=[states.SUCCESS]`
- R7 `set_started_and_completing_soon` future timestamp
- R6 `_apply_completed_meta` must not `set_completed()` on FAILURE (only merge; set
  `error`/`completed_datetime`)
- R12 dangling `F('result_capture_attempts')` increment (save it, or move to explicit
  counter update)
- R9 `update_count_progress` zero-target guard
- R13 `merge()` extras + deep `data` merge
- R15 `is_processing` excludes `REJECTED`/`IGNORED`

Acceptance: full `just test-app django_spire/celery` green (except the 4 known-failing
tracker tests, which phase 2 rewrites).

### Phase 1 — schema

One new migration in `django_spire/celery/migrations/`: `task_id unique`,
`runner_managed`.

Acceptance: applies to a fresh test DB; existing rows default `runner_managed=False`.

### Phase 2 — runner + tracker restructure

New files: `state_machine.py`, `runner.py` (runner + `spire_task`).
Modified: `meta.py` (4.2), `result.py` (4.6 `CeleryExceptionResult`), `tracker.py`
(4.4, incl. flusher + `data_model` validation), `models.py` (result property pure
read, `exception_result` properties, new field),
`test_project/app/celery/celery/tasks.py` (port the 6 tasks to `@spire_task`, incl.
typed `data_model`s), `tests/test_tracker.py` (rewrite the 4 failing tests to assert
tracker behavior: final meta merged into the claimed row, no `sleep(2)`, ordered
flushes).

Acceptance: §6 phase-2 test list green; a live worker run of a migrated task shows the
row reaching SUCCESS with the real return value in `_result`, meta.data intact, no
backend dependency for the UI; a failing task shows `exception_result.message` in the
UI.

### Phase 3 — web read-only

Files: `views/task_views.py`, `models.py`, templates (failure message from
`exception_result`), `admin.py` (readonly `exception_result`).

Acceptance: GET requests on runner rows never write (assert with a save-spy); legacy
rows still sync via the old path.

### Phase 4 — manager soft dedup + settings

Files: `manager.py`, `test_project/app/celery/celery/managers.py` (opt in at least
`PirateSongCeleryTaskManager` for the demo), `test_project/celery.py`
(`worker_deduplicate_successful_tasks=True`).

Acceptance: opted-in manager reuses the unready row on a second send; a completed row
frees the slot; non-opted-in managers unchanged.

### Phase 5 — optional extras (pick what you need, each its own small PR)

- `task_revoked` signal → CAS row → `REVOKED` + `check_revoked()` helper for loops
- metrics on terminal transitions (`Spire.Metric.Statistic.record`)
- stale-STARTED reaper management command (worker-died rows; uses `meta.last_update_time`)
- migrate `SEND_FAILED` dicts to `CeleryExceptionResult`
- (only if ever wanted) custom result backend writing straight to the `CeleryTask`
  model — decided NOT to do in this iteration; mirror stays

## 6. Test plan

Existing: `tests/test_tracker.py` (4 failing tests rewritten), `test_services/`,
`test_async_result_integration.py`, `test_querysets.py`, `test_models.py`,
`test_views.py` — all stay green.

New (phase 2):

- state machine: full transition table (allowed/denied), terminal stickiness,
  PENDING-regression rejection, custom states (custom→custom, custom→terminal,
  custom→STARTED rejected), `STARTED → RETRY` allowed
- out-of-order/duplicate snapshots: latest snapshot applied, progress never
  decreases, double terminal write dropped
- duplicate claim: two runner instances, same `task_id` → exactly one claim, the
  other raises `Reject(requeue=False)`; row written once
- result integrity: final `_result` is the task's return value, never a meta dict,
  even with a mocked slow backend mirror
- exception result: failing task → `_result` is a `CeleryExceptionResult` with
  exc_type/message/traceback; `exception` restores the original when picklable;
  non-picklable exception → traceback-only fallback; `result` still None
- data validation: `set_data` with bad key/type raises `ValidationError`; no
  `data_model` → free-form still works
- redelivery: second execution of a `STARTED` row → abort, no double result
- retry: `self.retry()` → row `RETRY`, `meta.retries=1` → second attempt re-claims
  STARTED
- eager mode (`apply()`): row is written, function returns
- untracked mode (direct `task()` call): no row access, no errors
- flusher: coalescing (100 `set_data` in 100ms → few writes, latest wins), ordering,
  `finish()` drains before returning, join-timeout surfaces as a logged failure
- tracker API compatibility: the 6 existing task bodies (minus `set_completed`)
  behave identically under the runner

New (phase 4):

- soft dedup: opted-in manager reuses unready row; freed after completion;
  non-opted-in unaffected

Infrastructure: unit tests with a fake task/`request` (as `test_tracker.py` already
does) + lifecycle integration tests via `task.apply()` (eager — no broker needed)
against the real Postgres test DB (port 5439); manual live verification with
`just celery` during phase 2.

## 7. Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| Flush thread per task at high concurrency | Fine at current scale (threads pool, `worker_max_tasks_per_child=200`); swap to one shared dispatcher thread later — tracker interface unchanged |
| `select_for_update` needs a real DB | Tests run on Postgres 5439; the swap to optimistic retry is local to `_apply_to_row` |
| Chords/canvas | Backend mirror still written, so `mark_as_done`/`on_chord_part_return` keep working |
| `task_track_started` auto-STARTED on the mirror | Harmless; no template path may read the backend for runner rows (verify in phase 3) |
| Worker dies between claim and first flush | Row stuck in STARTED → shown as processing; phase-5 reaper command if ever needed |
| Backwards compatibility with in-flight legacy tasks | `runner_managed` flag splits behavior; legacy path untouched until tasks migrate |
| Tracker/runner split seam | Tracker is only ever constructed by the runner (or tests); `_merge_meta_into_celery_task` is the single row-write path |
| `ExceptionInfo.pickle()` on exotic exceptions | try/except fallback to traceback text only; never let failure-recording fail the task's own failure path |
| `data_model` validation strictness | `model_validate` on the merged dict; unknown keys follow the model's `model_config` (default: ignore, matching today's free-form behavior) — opt into `extra='forbid'` per data model when wanted |
| Soft dedup residual race (two simultaneous sends) | Accepted — identical to today's behavior; hard index available later if ever needed |

## 8. Decision log

| # | Question | Decision |
|---|----------|----------|
| 1 | Delivery scope | **All phases 0–5** (phase 5 = pick-what-you-need) |
| 2 | Fate of `CeleryTaskTracker` | **Stays a separate component** — runner runs, tracker tracks (§4.3/§4.4); the `celery_task_model` stub becomes live |
| 3 | Duplicate-execution policy (redelivery) | **Abort, hard-coded** — `Reject(requeue=False)`; no config knob |
| 4 | Result backend (`db+`, separate DB) | **Keep as best-effort mirror** (AsyncResult/chords compat); no custom backend this iteration |
| 5 | Send-time dedup | **Per-manager opt-in, soft** — manager reuses the unready row; no DB index (residual race = today's behavior) |
| 6 | Typed `meta.data` validation | **Now (phase 2)** — `data_model` pydantic model per task, validated in `tracker.set_data` |
| 7 | Custom states ('MAKING NOISES') | **Keep free-form** in the row `state` column; state machine allows them from any non-terminal state |
| 8 | Failure rows in `_result` | **`CeleryExceptionResult`** (sibling of `CeleryNoResult`), built from `ExceptionInfo.pickle()`; `CeleryTask.exception_result` property; `.result` stays None for failures |
| 9 | Web polling | **Keep as-is** — runner rows become pure DB reads; no polling architecture change |
| 10 | Metrics | **Phase 5 optional** |
| 11 | Manual `set_completed()` in task bodies | **Removed from migrated bodies** — runner `finish()` is the terminal; a mid-run `set_completed()` is just a scheduled update |
| 12 | KISS schema review | **Minimal schema**: only `task_id unique` + `runner_managed`; hostname/retries in meta; no `meta_version` / `last_update_datetime` / `worker_hostname` / `retries` / `dedupe_enabled` columns; no partial unique index |
| 13 | Extension points | **Celery-native** — override `on_success`/`on_failure`/`on_retry` or connect `task_*` signals; no custom before_run/after_run hooks |
| 14 | State guarding | **Explicit transition table only** — precedence-based monotonic check rejected (it breaks `STARTED → RETRY`) |
| 15 | Structural trims | No `_RunContext` class (thread-local holds the tracker); flusher folded into `tracker.py`; `spire_task` in `runner.py`; no `CeleryTaskService` write/read split; module-level flush timeout constant |

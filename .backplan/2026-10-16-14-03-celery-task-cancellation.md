# celery task cancellation — 2026-10-16-14-03

Status: Executed

## End state

A CeleryTask in PENDING, RECEIVED, STARTED, RETRY, or a custom (progress)
state can be canceled from the task UI, the API, or the Django admin; the
`CeleryTask` record transitions to the existing sticky `REVOKED` terminal
state (rendered as "Canceled" in the task UI), the `celery_task_canceled`
metric fires exactly once per transition, and the worker receives
`revoke(task_id, terminate=True)` so a started task actually stops. Tasks in
a terminal state cannot be canceled and the three surfaces report that.

## Completion test

1. `just test-app django_spire/celery` passes, including new cases proving:
   - `CeleryTaskService.cancel()`: happy path publishes revoke + row becomes
     REVOKED with `completed_datetime` set + `celery_task_canceled` metric
     fires once; terminal row (any READY_STATES) → error, row unchanged;
     revoke publish failure → error, row unchanged.
   - cancel view: login required (302), `change_celerytask` required (403),
     200 JSON on success, 409 on already-terminal, 404 on unknown task.
   - API: `POST /api/v1/celery/tasks/{task_id}/cancel` → 200
     `{'state': 'REVOKED'}`; repeat → 409; unknown task → 404; key without
     change permission → 403/401.
   - admin action cancels selected non-terminal tasks, skips terminal ones
     with a per-task message.
   - UI: `is_canceled` property + the "Canceled at ..." content branch
     render for REVOKED rows; the cancel button shows only for
     pending/processing rows with change permission.
2. `just python manage.py makemigrations --check --dry-run` →
   `No changes detected` (no schema/choices change: REVOKED is already in
   the state choices).
3. `ruff check` / `ruff format --check` clean on touched files.
4. Live smoke on the dev worker (threads pool, RabbitMQ):
   - queued `pirate_noise_task` canceled → never runs, row REVOKED, UI shows
     "Canceled".
   - running `pirate_noise_task(length=60)` canceled → row REVOKED, worker
     stops the task (`inspect().active()` no longer lists it), UI shows
     "Canceled".
   - API + admin paths produce the same row state.

## Current state

Verified facts (2026-10-16, branch `nathanj/celery-update`, working tree
clean at `02d510d1`):

- `REVOKED` is the right existing state (no new state needed):
  - state machine `BASE` already allows PENDING/RECEIVED/STARTED/RETRY →
    REVOKED and `REVOKED: set()` (state_machine.py:14-20); custom states
    reach it through the STARTED anchor (test_state_machine.py:70)
  - REVOKED is in celery `READY_STATES`, so the single-writer sticky
    checks, the admin state filter, and `state_verbose` already cover it
  - `by_unready()` (READY+EXCEPTION excluded) and `is_processing` already
    treat it as non-active, so `dedupe_unready` will not reuse it
  - nothing in the codebase produces a REVOKED row today (only test
    fixtures: test_async_result_integration.py:66, test_querysets.py:123);
    in this architecture the worker never writes terminal states, so only
    the cancel path can create one
- Celery 5.6.3 (venv):
  - `app.control.revoke(task_id, terminate=True)` is the standard stop
    mechanism: queued tasks are discarded at dispatch, started tasks are
    signaled
  - a revoked queued task produces **no** terminal backend write; the web
    record is the only place REVOKED can come from
- `django_spire/celery/services/service.py` (single writer):
  - `_apply_backend_snapshot()` under `select_for_update`; terminal branch
    `if state in states.READY_STATES`; metric gate
    `records_metric = state in _METRIC_REFERENCES and fresh.state not in
    states.READY_STATES`
  - `_METRIC_REFERENCES` = {SUCCESS: 'celery_task_success', FAILURE:
    'celery_task_failure', RETRY: 'celery_task_retry'} →
    `StatisticTrackingService.track_configured(reference=...)`; REVOKED not
    yet mapped
  - `update_from_backend()` sticky early-return already returns for REVOKED
    rows; note its lazy result backfill (`_capture_result_lazy` on backend
    SUCCESS + `has_no_result`) applies to every terminal row and will
    backfill a REVOKED row whose task completed in the dispatch race (see
    edges below)
- `django_spire/celery/models.py`:
  - `state` CharField(32), choices from `states.ALL_STATES` (REVOKED
    included, models.py:16-17)
  - `is_pending/is_successful/is_failed` are single-state checks; no
    `is_canceled`; `is_processing` already excludes REVOKED
- `django_spire/celery/views/task_views.py` + `urls/task_urls.py`:
  - only item/toast/item_list/toast_list fragment views, `login_required`
    only, no permission decorator, no POST/action views
- `django_spire/celery/admin.py`:
  - `CeleryTaskStateFilter` lists `states.ALL_STATES` + observed states
    (REVOKED included, no change needed)
  - no admin actions; `has_add_permission` returns False
- `django_spire/celery/apps.py`: no `API_V1_ROUTER`/`API_V1_ROUTER_PREFIX`
  (the celery app has no API surface yet)
- Web→broker precedent: `prune_stale_started_celery_tasks.py` uses
  `from celery import current_app` + `current_app.control.inspect(...)`
- Metrics: references are plain strings resolved by
  `StatisticTrackingService.track_configured(reference=...)`; no registry
  entry needed for `celery_task_canceled`
- UI mechanics:
  - `task_item_list.html` wrapper re-renders via
    `Glue.view(item_url).renderInnerHtml($el, {})`
  - AJAX POST pattern: `Spire.ajax.request('POST', url)` with X-CSRFToken
    from the csrftoken cookie (core/static/django_spire/js/ajax.js:8)
  - `task_content.html` branches on is_pending/is_processing/is_successful/
    is_failed; included by both item and toast templates
- Permissions:
  - `@permission_required('...')` (django_spire/auth/permissions/decorators.py)
    redirects anonymous to login, raises PermissionDenied otherwise
  - CeleryTask app_label = `django_spire_celery` → codename
    `django_spire_celery.change_celerytask` (Django model perms, already in
    migrations)
- API house pattern:
  - `django_spire/api/api_v1.py:21-33` auto-discovers app
    `API_V1_ROUTER` + `API_V1_ROUTER_PREFIX`
  - per-endpoint `ApiKeySecurity(api_permission_required=...,
    user_permission_required=...)` (test_project/app/task/api_v1.py)
  - API test pattern: test_project/app/task/tests/test_api_v1.py
    (ApiAccess + `HTTP_X_API_KEY`)
- Admin house pattern: `@admin.action` (knowledge/entry/admin.py)
- Environment:
  - dev worker = threads pool (`just celery`); broker RabbitMQ
    (rabbitmq.compute.stratusadv.com), result backend PostgreSQL
  - threads-pool caveat: `revoke(terminate=True)` signals the worker
    **process**, so stopping one started task can kill the whole dev worker
  - test app has long-running `pirate_noise_task(length)` for smoke testing
- House style: ruff (ALL, single quotes, 100 cols), no code comments,
  `just` for all commands

## Plan

1. `CeleryTaskService.cancel()` (the single cancel path) + metric mapping
   - `_METRIC_REFERENCES` gains `states.REVOKED: 'celery_task_canceled'`
   - `cancel()` on CeleryTaskService, order matters:
     publish `current_app.control.revoke(str(task_id), terminate=True)`
     first (broker failure → return error, row unchanged); then claim the
     transition to `states.REVOKED` atomically under `select_for_update`
     guarded by `CeleryTaskStateMachine.ok` (already-terminal → return
     error, row unchanged); on success set `state=REVOKED`,
     `completed_datetime=now()`, keep meta/`_result` as-is, sync `self.obj`,
     then fire `_record_terminal_metric(states.REVOKED)` exactly once
   - done when service tests pass: happy path (revoke published, row
     REVOKED, reference 'celery_task_canceled' fired once), terminal reject,
     revoke-failure reject
2. UI surface
   - `models.py`: new `is_canceled` property (`state == states.REVOKED`)
   - `task_cancel_view(request, task_id)` in task_views: `login_required` +
     `@permission_required('django_spire_celery.change_celerytask')`, POST
     only, JSON responses (200 `{'canceled': True}` / 409 `{'error': ...}` /
     404); URL `cancel/<str:task_id>/` name='cancel'
   - `task_content.html`: cancel button (stop icon) shown for
     pending/processing rows where the user has change permission
     (`perms` + state checks); handler POSTs via `Spire.ajax.request` and
     re-renders the item via the existing `Glue.view(...).renderInnerHtml`
     pattern; new "Canceled at ..." body branch (stop-circle icon, muted
     color) for `is_canceled`
   - done when view tests pass (login 302, no-perm 403, success 200 + revoke
     mocked + REVOKED row, terminal 409, unknown 404), the button
     shows/hides per permission and state, and a rendered REVOKED item shows
     the "Canceled at ..." line
3. API surface
   - New `test_project/app/celery/api_v1.py` (example for people to follow,
     mirroring `test_project/app/task/api_v1.py`):
     `POST tasks/{task_id}/cancel` with `ApiKeySecurity(
     api_permission_required=ApiPermissionChoices.CHANGE,
     user_permission_required='django_spire_celery.change_celerytask')`;
     200 `{'task_id', 'state'}`, 409 on already-terminal, 404 on unknown
   - `test_project/app/celery/apps.py`: `API_V1_ROUTER =
     'test_project.app.celery.api_v1.router'`, `API_V1_ROUTER_PREFIX =
     'celery'` (auto-discovered by the shared NinjaAPI)
   - done when API tests (modeled on test_project/app/task/tests/test_api_v1.py)
     pass: 200 cancel, 409 repeat, 404 unknown, insufficient key rejected
4. Admin surface
   - `@admin.action` "Cancel Selected Celery Tasks" (change permission) in
     CeleryTaskAdmin: calls `services.cancel()` per selected task, success +
     skip messages via the message framework
   - done when admin tests pass (action cancels queued/started, skips
     terminal with a message, requires change permission)
5. Suite + lint (no migration)
   - `just test-app django_spire/celery`
   - `just python manage.py makemigrations --check --dry-run` → No changes
   - `ruff check` / `ruff format` on touched files
   - done when the whole celery suite is green and ruff is clean
6. Live smoke test
   - `just celery` (threads pool) + dev server; cancel a queued and a
     running `pirate_noise_task` from UI, API, and admin; verify DB state,
     worker activity, and rendered UI in all three cases
   - done when the completion-test smoke checklist (step 4) is observed

Risky step: 1 — the revoke-publish/DB-claim race plus the single-writer
terminal path it hangs on. Known edges, by design:
- a task already dispatched when the revoke lands may still run to
  completion; the record stays REVOKED (sticky) and its backend result is
  discarded by the transition. The existing lazy result backfill in
  `update_from_backend()` can then fill the row's result column while the
  state remains REVOKED — same behavior every terminal row already has.
- broker down at cancel time → publish fails, nothing changes, error surfaced
- threads pool: `revoke(terminate=True)` cannot actually kill the task thread.
  Observed (Celery 5.6.3): `celery/concurrency/thread.py` implements no
  `kill_job`, so the worker's pidbox revoke handler logs
  `NotImplementedError: TaskPool does not implement kill_job` after printing
  "Terminating <id> (15)"; the thread runs on and the native tracer writes a
  late terminal (e.g. SUCCESS) to the backend. The record stays REVOKED
  (sticky; the late transition is dropped with a logged warning) — the
  documented limitation, no code change

Naming notes:
- state = `REVOKED` (celery's own terminal state for this operation; it was
  already wired through the state machine, sticky checks, querysets, choices,
  and admin filter with no competing producer) — decided 2026-10-16 after
  the initial CANCELED draft
- user-facing wording = "Canceled" (task UI body line + cancel action copy);
  admin state display stays "Revoked" via `state_verbose`
- metric reference = `celery_task_canceled` (maps from the REVOKED state in
  `_METRIC_REFERENCES`)

## Deviations

1. Plan re-derived before execution: initial draft proposed a new CANCELED
   state; switched to the existing REVOKED terminal state at 2026-10-16 14:0x
   after confirming nothing produces REVOKED rows today and the
   state machine/terminal handling already cover it.
2. The threads-pool edge in the plan assumed terminate would signal the whole
   worker process; observed behavior is that the thread pool implements no
   `kill_job` (NotImplementedError in the pidbox handler), so the task thread
   runs to completion and its late terminal is discarded by the sticky
   REVOKED row. No code change; the plan's known-edges list was corrected.
3. `django_spire/celery/api_v1.py` is a single module (not the
   `api_v1/router.py` package the plan sketched) — same router surface,
   simpler layout.
4. `django_spire/celery/api_v1.py` shipped in the framework package
   initially; user corrected at 2026-10-16 that the API belongs in the test
   project as a reference example. Moved to `test_project/app/celery/api_v1.py`
   (same router, prefix, URL path, and reverse name — all 7 API tests moved
   to `test_project/app/celery/tests/test_api_v1.py` and pass at the new
   location; live re-check of the moved endpoint returned 200/REVOKED + 409
   on repeat). Framework `apps.py` no longer declares `API_V1_ROUTER`.
5. Cooperative cancellation was explored in depth (custom control command +
   per-task event, USR1 signal, result-backend flag, stock AbortableTask) and
   explicitly dropped by the user at 2026-10-16; hard-terminate only shipped.
6. UI cancel button shipped with no in-flight feedback (user report
   2026-10-16): added a `canceling` Alpine state (spinner swap, dim +
   pointer-events lock, double-click guard), success toast
   ("Task '...' canceled") and an error toast carrying the server's 409
   message, and the post-cancel re-render now calls the wrapper's own
   `reload_task()` instead of a querySelector/classList guess. Supporting:
   `Spire.ajax.request` now parses the response body on non-ok responses too
   (additive; the thrown result carries `data`), so clients can surface
   server error messages.
7. Dev worker pool switched threads -> prefork and the `just celery` recipe
   now gets a unique hostname per start (user asked 2026-10-16 to adjust
   `just celery`): recipe is
   `... worker -l info --pool=prefork --hostname spire-dev-{{ uuid() }}@%h`.
   Two separate live findings drove this:
   - threads pool cannot kill a running task (no `kill_job`), so
     terminate-only cancellation never actually stops dev tasks; prefork
     children can.
   - while verifying terminate on prefork, service-path cancels failed to
     reach the worker running the task. Root cause via `ps aux` + kombu
     boot warnings ("A node named celery@not-a-toaster is already using
     this process mailbox!"): several local worker processes shared the
     node name `celery@not-a-toaster`, and RabbitMQ load-balances the
     revoke pidbox cast across same-named consumers, so most revokes hit a
     process not running the task ("terminate: tasks unknown", no log
     line, task runs on; observed kill rate ~1/3, consistent with 3
     consumers). The unique per-start hostname isolates each worker's
     pidbox mailbox, so the broadcast can only land on that worker.
   - the threads-pool limitation remains documented for threads
     deployments; the dev default is now prefork.

## Completion

Observed output (2026-10-16):

- `just test-app django_spire/celery` → `324 passed in 9.30s` (12 workers);
  `just python -m pytest test_project/app/celery --reuse-db` → `7 passed`
  (the API tests, moved to the test project per user correction)
- `just python manage.py makemigrations --check --dry-run` →
  `No changes detected`
- `ruff check` on all touched files → only the 4 pre-existing findings
  (`admin.py:21/31/104` ARG002, `models.py:26` DJ001); `ruff format --check`
  clean
- Live smoke (`just celery` threads pool + dev RabbitMQ cluster, Django test
  client — no curl):
  - queued `pirate_noise_task` (eta) canceled via UI → 200
    `{"canceled": true}`; row REVOKED with `completed_datetime`; after the eta
    the worker log shows `Discarding revoked task: pirate_noise_task[...]`,
    row still REVOKED, backend REVOKED (never ran)
  - queued `ninja_attack_task` (eta) canceled via the admin action → row
    REVOKED, changelist shows `Canceled 1 Celery Task(s)`; after the eta the
    worker discards it, row still REVOKED (never ran)
  - running `pirate_noise_task` canceled via API (`X-API-Key`) → 200
    `{"task_id": "...", "state": "REVOKED"}`; row REVOKED with
    `completed_datetime`; worker log shows `Terminating <id> (15)` followed by
    the threads-pool `kill_job` NotImplementedError (documented limitation)
  - running task (custom state `MAKING NOISES`) canceled via UI → listed in
    `inspect().active()` pre-cancel, 200, row REVOKED + `is_canceled`; after
    the thread ran out the backend showed SUCCESS while the row stayed
    REVOKED — the designed result-discard edge, observed
  - cancel of an already-SUCCESS row → 409
    `{"error": "Task already finished with state Success"}`, row unchanged
    (dispatch race handled)
  - rendered `task_item.html` for a REVOKED row shows `Canceled at ...` and
    the `bi-stop-circle-fill` stop icon
- Live terminate verification (2026-10-16, after the pool/hostname fix in
  deviation 7): dedicated prefork worker on a unique node name
  (`spire-smoke-a1b2c3d4@not-a-toaster`, `-Q celery_smoke --concurrency=2`,
  no "process mailbox" warning at boot; only consumer of `celery_smoke`),
  3x service-path cancels of `pirate_noise_task(length=90)` sent via
  `app.send_task` with a fresh `CeleryTask` row per run:
  - every run: row PENDING -> STARTED, `POST .../task/cancel/<task_id>/`
    -> 200, row REVOKED immediately, still REVOKED 15s later, and still
    REVOKED after the acks-late re-queued copy ran to completion (late
    backend SUCCESS discarded by the sticky row, as designed)
  - worker log shows `Terminating <tid> (15)` for all three tids — 3/3
    kills, versus the 2/5 kill rate with duplicate node names and 0
    effective kills on the threads pool
- Full default suite re-run after the justfile hostname change:
  `just test` -> 4495 passed (no behavior change from the recipe edit)

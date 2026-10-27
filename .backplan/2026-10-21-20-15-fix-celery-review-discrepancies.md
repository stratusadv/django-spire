# Fix Celery review discrepancies

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-21-20-15

## End State

All 13 discrepancy rows from the completed review (`.backplan/2026-10-21-15-05-validate-celery-module-operation.md`,
rows #1-#13) are closed in code, tests, and docs: the celery module passes its full test suite
plus `ruff check .`, a local pre-commit hook demonstrably blocks a bad commit and passes a clean
one, and AGENTS.md/changelog describe the new behavior. Nothing is committed.

## Observable Concern

The process-detection rewrite (row #4) changes which processes start the scheduler/sweep threads:
if the allow-list is too narrow, real web deployments (WSGI/ASGI servers) silently lose their
cron + sweep threads; if too wide, the F-1 worker-thread defect survives. The detection matrix
must be pinned by tests before any other step ships.

## Confirmed Intent (user-answered, 2026-10-21)

- Scope: **all 13 discrepancy rows** (critical + major + minor/informational).
- Row #8 (broken commit): fix with a **local pre-commit hook** running ruff on staged files.
- Row #9 (PG14 dev DB vs Django 6.1): **out of scope - the user is fixing the environment
  themselves.** The fix must not assume the dev DB is usable by new Django processes (tests run
  against the docker PG16 test DB as before).

## Current State (verified)

- `process.py:10-18` - `is_web_server_process()`: `RUN_MAIN=='false'` -> False; `argv[0] !=
  manage.py` -> **True (the bug: workers, scripts, unknown binaries all count as web)**; else the
  first non-flag argv must be in `{runserver, runserver_plus}`. Used exactly twice:
  `sweep.py:83` and `scheduler.py:226`. No other references.
- `apps.py:28-35` - `ready()` calls `start_scheduler()` + `start_sweep()` unconditionally; the
  enable flags + process gate live inside each `start_*`.
- `sweep.py:79-102` / `scheduler.py:219-245` - `start_sweep`/`start_scheduler` return False when
  disabled, misconfigured, or `not is_web_server_process()`.
- `runner.py:6,15` - `CeleryTaskRunner(DjangoTask)`; `DjangoTask` (celery.contrib.django.task)
  adds only `delay_on_commit`/`apply_async_on_commit`; grep: **zero `on_commit` usage** in
  django_spire - the base buys nothing and drags `django.db` into every worker.
- Metrics - `service.py:31-36` `_METRIC_REFERENCES` (4 references incl. `celery_task_canceled`);
  fired only from `_apply_backend_snapshot` (via `update_from_backend` :204-207) and `cancel`
  (:233). **No metric** on: reaper FAILURE stamp (`prune_stale_started_celery_tasks.py:87-90`,
  direct `.update()`) or send-failure row creation (`manager.py:175-195`).
  `StatisticTrackingService.track_configured(reference=...)` at
  `metric/domain/statistic/services/tracking_service.py:104`.
- Reaper - `prune_stale_started_celery_tasks.py`: STARTED-only collection (:102-109, empty meta
  = stale at any threshold); triage backend-terminal -> `update_from_backend()` (metric fires),
  active-on-worker -> skip, else FAILURE stamp (:87-90, no metric); `_active_task_ids()` (:123-141)
  cannot distinguish "workers say it's gone" from "no workers responded at all" (`inspect().active()`
  returns `{}` in both cases) - the redelivery divergence (row #6).
- `manager.py:123-161` - send path; dedupe check-then-act :133-139 (non-atomic, row #13);
  send retries + backoff :141-157; `_create_failed_celery_task` :175-195.
- `scheduler.py:120-150` - `claim_schedule_slot`: claim UPDATE and send are separate; the claim
  win is logged only indirectly via the later 'Sent scheduled task' line (row #7).
- Settings - `django_spire/settings.py:23-30`: `DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES/ENABLED/
  TICK_SECONDS`, `DJANGO_SPIRE_CELERY_SWEEP_ENABLED/INTERVAL_SECONDS/TASK_LIMIT` (defaults 20s/20).
  `test_project/celery_settings.py` enables both + registers `TestProjectScheduler`.
- Docs - `AGENTS.md:20` says `just celery` = "threads pool" but the justfile (:14) runs
  `--pool=prefork`; `AGENTS.md:415` lists 3 terminal metrics (code has 4); `AGENTS.md:463` reaper
  paragraph and :478 scheduler paragraph predate rows #2/#4/#5/#6/#7/#12.
- Changelog - `docs/changelog/changelog.md` top entry `v1.3.0` (Features/bugfixes format).
- Tooling - no pre-commit framework in the repo, no custom git hooks (`.git/hooks` samples only),
  no ruff recipe in the justfile (AGENTS.md runs `ruff check .` directly), ruff.toml `select
  = ["ALL"]`.
- Test house style - `django_spire/celery/tests/`: pytest `@pytest.mark.django_db` classes,
  `unittest.mock.patch` of `sys.argv`/settings, factories in `tests/factories.py`, reaper tests in
  `test_commands.py` (TestCase-based).

## Plan

1. **Process detection (closes #4 root cause, #1)**
   - Rewrite `process.py::is_web_server_process()`: env override first
     (`DJANGO_SPIRE_CELERY_WEB_PROCESS` = true/1/yes -> True, false/0/no -> False, unset ->
     auto-detect); then `RUN_MAIN=='false'` -> False; then `argv[0]` basename `manage.py` -> first
     non-flag arg in `{runserver, runserver_plus}`; else `argv[0]` basename in
     `{gunicorn, uwsgi, uvicorn, daphne, hypercorn}`. Everything else (celery workers, scripts,
     other manage.py commands, unknown binaries) -> False.
   - New `tests/test_process.py`: full detection matrix (runserver parent/child via RUN_MAIN,
     runserver_plus, gunicorn, uvicorn, manage.py migrate/shell, `python -m celery` worker argv,
     console `celery` binary argv, `python script.py`, env override both ways).
   - Done when the matrix is green and `start_sweep`/`start_scheduler` inherit the gate unchanged
     (existing tests still pass).
2. **DjangoTask base swap (closes #3)**
   - `runner.py`: import `Task` from `celery.app.task` and base `CeleryTaskRunner` on it; delete
     the `DjangoTask` import.
   - Test in `test_runner.py`: `CeleryTaskRunner` is a `celery.app.task.Task` subclass and NOT a
     `DjangoTask` subclass.
   - Done when the celery suite passes and a worker-side import closure check (existing portability
     style) shows no `django.db` via the runner.
3. **Shared terminal-metric helper + missing emissions (closes #5)**
   - New `django_spire/celery/metrics.py`: `TERMINAL_METRIC_REFERENCES` (the 4 references, moved
     from service.py) + `record_terminal_metric(state)` (lazy import of
     `StatisticTrackingService.track_configured`, try/except + warning, same as today).
   - `service.py`: import the helper, drop the local dict, `_record_terminal_metric` delegates.
   - Reaper: after the FAILURE stamp `.update()`, call `record_terminal_metric(states.FAILURE)`
     once per stamped row (exactly-once holds: re-runs find no STARTED rows).
   - `manager.py::_create_failed_celery_task`: record `states.FAILURE` after row creation (fires
     exactly once per failed send; dedupe-reuse path returns the existing row and records nothing).
   - Tests: reaper stamp fires the metric N times for N rows (mocked `track_configured`);
     send-failure fires once; dedupe-reuse fires zero; service path unchanged.
   - Done when the 24h-audit invariant (row terminals == metric events) holds by construction on
     all three write paths, covered by tests.
4. **Reaper: PENDING coverage + no-workers guard (closes #2, #6)**
   - `--include-pending` flag: with it, also collect stale PENDING rows (same empty-meta/stale
     threshold rule). Triage: backend terminal -> `update_from_backend()` (sync + exactly-once
     metric - heals the live F-2 case); backend non-terminal -> **skipped with a log, never
     FAILURE** (acks_late requeue hazard: a queued-but-not-consumed message could still run).
     STARTED triage unchanged.
   - No-workers guard (applies to STARTED failure candidates, as today, but now correct): before
     stamping, `inspect().ping()` - if the response dict is empty (no live worker responded) skip
     ALL failure candidates with an explicit log ("no live workers; task may still be requeued"),
     because an unacked message is sitting in the broker waiting for a worker. If workers respond
     and none reports the task active, stamp as today.
   - Tests: PENDING+terminal-backend syncs with the flag; PENDING skipped without the flag;
     PENDING+non-terminal skipped (never FAILURE); ping `{}` -> no stamp; ping non-empty + not
     active -> stamp.
   - Done when both live-divergence scenarios from the review (7b402c1e-style stale PENDING;
     6d67dbd1-style stamp-while-requeued) are covered by tests.
5. **Claim audit log (closes #7)**
   - `scheduler.py::claim_schedule_slot`: on a won claim, log INFO with schedule_key, slot time,
     and claimed_by before sending. (The unloggable part - process death between claim and send -
     is documented as accepted at-most-once behavior; the claim row + this log form the audit
     trail.)
   - Test: claim win logs the line (caplog), lost claim does not.
   - Done when a lost slot is reconstructable from logs + the claim row.
6. **Thread liveness command (closes #12)**
   - New management command `check_celery_threads`: for the sweep, stale iff
     `now - CeleryTaskSweep.last_swept_datetime > max(DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS *
     2, --max-age default derived)`; for the scheduler, for each registered entry compute the next
     due slot from its `last_sent_datetime` via the same crontab math the loop uses and stale iff
     that slot is in the past by more than a grace bound. Prints per-component OK/STALE lines;
     `--fail` exits 1 when anything is stale (cron/monitoring friendly). Components that are
     disabled by settings report SKIPPED.
   - Tests: fresh rows -> OK; old sweep row -> STALE; scheduler entry past due -> STALE; disabled
     -> SKIPPED; `--fail` exit code.
   - Done when a dead web process or dead thread turns into a non-zero exit within one check
     interval.
7. **Pre-commit hook (closes #8)**
   - `scripts/git-hooks/pre-commit` (POSIX sh, executable): collect staged `.py` files
     (`git diff --cached --name-only --diff-filter=ACM`), run `.venv/bin/ruff check` on them
     (skipping files deleted from the working tree), block the commit on any failure; exit 0 when
     no Python files are staged.
   - `justfile` recipe `install-hooks`: `git config core.hooksPath scripts/git-hooks`.
   - AGENTS.md Setup section: one line - run `just install-hooks` once.
   - Verification (no commit made): stage a scratch Python file with a lint violation -> hook
     exits non-zero; fix it -> hook exits 0; unstage + delete the scratch file; run
     `just install-hooks` so the hook is live for the user.
   - Done when a bad staged file demonstrably blocks and a clean one passes, with the tree left
     uncommitted.
8. **Docs + changelog (closes #10, #11, #13; documents everything else)**
   - AGENTS.md: :20 comment "threads pool" -> "prefork pool"; :415 terminal-metric list gains
     `celery_task_canceled` (4 metrics); :463 reaper paragraph updated (`--include-pending`,
     no-workers guard, terminal metric on stamps, PENDING rows are synced-never-stamped); :478
     scheduler paragraph - thread starts only in real web processes (runserver/runserver_plus or
     gunicorn/uwsgi/uvicorn/daphne/hypercorn; workers and scripts are excluded; env override
     `DJANGO_SPIRE_CELERY_WEB_PROCESS`); new `check_celery_threads` + `just install-hooks`
     mentioned; dedupe paragraph gains the known non-atomic window note (row #13: acceptable at
     current scale, documented, no code change).
   - `docs/changelog/changelog.md`: new `v1.3.1` entry (Bugfixes: worker/script thread start,
     reaper gaps, metric gaps; Features: liveness command, pre-commit hook, env override).
   - Done when every behavior changed in steps 1-7 is described accurately in AGENTS.md and the
     changelog.
9. **Completion test + close**
   - Run the completion test below, quote real output into this doc, set `Status: Executed`.
   - Leave the working tree uncommitted (user's in-flight pyproject/uv.lock upgrade untouched).

## Completion Test

1. `just python -m pytest django_spire/celery/tests/ --reuse-db -q` -> all passed (includes the
   new process/metrics/reaper/liveness tests).

   ```
   ============================= 449 passed in 9.46s =============================
   ```

2. `just test` -> all passed.

   ```
   ============= 4621 passed, 2 warnings, 4 subtests passed in 44.92s =============
   ```

   Both warnings are pre-existing and unrelated: the intentional legacy-activity
   `DeprecationWarning` asserted by the confirmation-form test, and a memcached `CacheKeyWarning`
   in the metric visual tests.

3. Lint -> see Deviation #1 (gate re-scoped from "`ruff check .` clean" to "no new violations vs
   the HEAD baseline in the celery tree; new files clean").

   ```
   $ diff /tmp/baseline_norm.txt /tmp/current_norm.txt   # rule-code histograms, celery tree
   (empty output: LINT_DIFF_CLEAN)
   $ .venv/bin/ruff format --check django_spire/celery/
   56 files already formatted
   $ .venv/bin/ruff check <every new file>
   All checks passed!
   ```

4. Hook rehearsal: staged lint-violating file -> `scripts/git-hooks/pre-commit` exited 1 (ruff
   reported `F401` + `RET504`, hook printed "ruff found problems in staged files; fix them or
   bypass with git commit --no-verify"); fixed file -> exit 0 ("All checks passed!"); no Python
   files staged -> exit 0; scratch file unstaged and deleted; `git config core.hooksPath` ->
   `scripts/git-hooks`.

   ```
   hook_exit=1
   hook_exit_clean=0
   hook_exit_nopy=0
   ```

5. `git status --short` shows only the intended framework/test/script/doc changes, the untracked
   pre-existing `django_spire/celery/tests/test_race_harness.py`, and the user's uncommitted
   `pyproject.toml`/`uv.lock`. `git log --oneline -1` -> `a2dfb58d indent typo` (HEAD unchanged,
   nothing committed).

## Deviations

1. **Lint gate re-scoped (completion test 3).** The user's in-flight `uv sync` (Django 6.0.6 ->
   6.1.2) pulled in ruff 0.17.1, which flags files this work never touched (`tools.py`,
   `admin.py`, `manager.py`, `models.py`, `templatetags`, `factories.py`, `__init__.py`,
   manager tests): verified the identical violation set on a pristine `git archive HEAD`
   (`/tmp/spire_head_baseline`). The "`ruff check .` -> clean" condition is re-scoped to: the
   rule-code histogram of `django_spire/celery/` is identical to the HEAD baseline (diff empty)
   and every new file is clean under `ruff check` + `ruff format`. The pre-existing dirt is the
   same class as row #9 (user's upgrade), left for the user's own cleanup.
2. **Extra doc accuracy fix (step 8).** The AGENTS.md state-freshness paragraph said the sweep
   interval "defaults to 30" and the task limit "caps each window at 100"; the settings defaults
   are 20 s / 20 (there is no 100 cap in code). Corrected to the actual defaults while updating
   the same paragraph for `check_celery_threads`.

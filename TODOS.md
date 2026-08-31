# TODOs — `django_spire.metric` Review

Review of all models, apps, and sub-apps inside `django_spire.metric` for scaling into the future, migration problems, traps, and gotchas. Each item is prioritized (critical/high first) with a file reference, the concrete work suggested, and a status column to be updated as items land.

**Verification pass (2026-08-30):** every item below was checked against the current source (models, services, middleware, migrations, API, views, templates, templatetags). `just test-app django_spire/metric` passes **415/415** — none of these is a currently failing test; they are latent correctness, migration, or scaling concerns. Items marked **confirmed** hold as written; items with caveats say so; the `Domain.sub_domain_name` item was **corrected**.

## Inventory

| App / package | Label | Models |
|---|---|---|
| `metric` | `django_spire_metric` | none (URL/router host) |
| `metric/domain` | `django_spire_metric_domain` | `Domain`, `SubDomain` + all 3 "statistic" models |
| `metric/domain/statistic` | ⚠️ *not an app* — models folded into `django_spire_metric_domain` | `StatisticGroup`, `Statistic`, `StatisticValue` |
| `metric/report` | `django_spire_metric_report` | `ReportRun` |
| `metric/visual` | `django_spire_metric_visual` | `Visual` (+5 proxies), `VisualCondition`, `VisualReference`, `VisualRegion` |
| `metric/visual/presentation` | `..._presentation` | `Presentation`, `Slide`, `SlideSection` |
| `metric/visual/signage` | `..._signage` | `Signage`, `SignagePresentation` (M2M through) |

---

## Critical / High

- [ ] **`StatisticValue` is an unbounded append-log with no uniqueness and no retention on the API path** — `django_spire/metric/domain/statistic/models.py:94` — *confirmed*
  - Migration `0002` **removed** the original `UNIQUE(statistic, reference, date)` constraint (`domain/migrations/0002_statisticvalue_sub_domain.py:41`) and never replaced it; `StatisticValue.Meta` (models.py:113-122) defines only the two composite indexes, no constraint. Every `add_value`/`increment`/`record` blindly `create()`s a row (`services/processor_service.py:49-51`). Duplicate calls are not idempotent — the same reference+timestamp recorded twice double-counts every aggregate.
  - The track path trims to `DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX` (default 1000; `services/tracking_service.py:52-60`), but the public `POST /record` API path calls `processor.add_value` with **no trim, no retention, no partition** — a consumer can grow this table forever.
  - `GET /{key}/values` returns **every row in the interval as an unbounded list** (`api_v1.py:124-145`). `StatisticValueIn.reference` (`api_v1.py:20`) has `min_length=1` but **no `max_length`** and no cardinality bound — one consumer can spawn unlimited distinct references and can 500 on a >255-char value.
  - **Suggested fix**
    - Pick one semantic: (a) keep it a raw event log and add idempotency, or (b) make `record` an upserted per-day aggregate. The least invasive for existing consumers: keep the log but re-add a uniqueness/idempotency hook and bound the API.
    - Re-add a constraint in a forward migration: `UniqueConstraint(fields=('statistic', 'sub_domain', 'reference', 'timestamp'), name='unique_statistic_value_reference_timestamp')` — makes duplicate `record` calls error on a clean 4xx (catch in the endpoint) instead of silently double-counting.
    - Add API-path retention: a scheduled task (Celery beat / management command) pruning `StatisticValue` rows older than `DJANGO_SPIRE_METRIC_RETENTION_DAYS` (mirror the trim already on the track path). Run it off the hot path.
    - Cap `GET /{key}/values`: add a `limit`/`offset` or page param (default e.g. 1000, max 5000) and document it.
    - Add `max_length=255` to `StatisticValueIn.reference` (and validate in `add_value`), so >255-char input returns 422, not 500.

- [ ] **Tracking writes + trims on the hot path every render** — `django_spire/metric/domain/statistic/middleware.py:57-77` — *confirmed, conditional on config*
  - Middleware is registered at `test_project/base_settings.py:161`; it is **only hot when `DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY`/`..._SUB_DOMAIN_KEY` are configured** (base_settings.py:48-49 from env; default empty in `django_spire/settings.py:55-56`; `test_settings` sets `''`) — otherwise `_dispatch_click` short-circuits (middleware.py:57-62) and the tracker never runs.
  - When enabled, every qualifying HTML GET spawns a **new daemon thread** that opens its own DB connection, `INSERT`s, then `count()`s + possibly `DELETE`s (`tracking_service.py:39-43, 52-60`; `_track_click_in_background` middleware.py:20-24). The trim `count()` filters on `(sub_domain, reference)` with `reference` unindexed — a scan per tracked request; count-then-delete on every track → write amplification + bloat.
  - **Suggested fix**
    - Replace thread-per-request with a bounded queue or a Celery task (single worker consumes, batches inserts) when tracking is enabled; keep the current code as the `cellery`/sync fallback.
    - Move the trim off the hot path: drop the per-track `count()`; trim in a scheduled task instead (which also gives retention for the API path). If trimming must stay on write, only check periodically (`track_count % N == 0`) and keep it in one `transaction.atomic()`.
    - Add the `(statistic, reference, timestamp)` index (next item) so the trim/`count()` scans, when they do run, use it.

- [ ] **`reference` has no index and the workload is reference-driven** — `django_spire/metric/domain/statistic/models.py:106` — *confirmed*
  - Chart/dashboard reads (`for_reference`, `for_reference_pattern`, `for_reference_patterns`, `series_datasets` per dataset, `breakdown` grouped by `reference`; querysets.py:99-117, 139-151) filter an unindexed `varchar(255)`; the only indexes are `(statistic, timestamp)` and `(statistic, sub_domain, timestamp)` (models.py:117-122). Wildcard patterns fall through to `reference__regex` (querysets.py:58), which a btree index cannot serve.
  - **Suggested fix**
    - Add `models.Index(fields=['statistic', 'reference', 'timestamp'], name='ix_statistic_reference_ts')` to `StatisticValue.Meta.indexes` + migration. This serves the exact, prefix/suffix/contains paths and the tracking trim.
    - If wildcard-pattern reads matter at scale, add a `pg_trgm` GIN index on `reference` (Postgres) to serve the `__regex`/`__contains` paths instead of scans. Exact-lookup semantics stay correct either way.

## Scaling

- [ ] **`interval_summary` aggregates in Python** — `django_spire/metric/domain/statistic/services/transformation_service.py:109-131` — *confirmed*
  - Pulls **every row in the date range into memory** and loops, re-deriving interval bucket starts per row and computing totals/averages in Python. `daily_summary`/`series_points`/`breakdown` (:61-77, :128-151 in querysets) do the equivalent in SQL.
  - **Suggested fix**
    - Make it SQL-native: group by day in SQL first (`TruncDate('timestamp')`, exact mirror of `daily_summary`), then reduce the ≤(days-in-range) day rows into interval buckets in Python — memory becomes O(days), not O(rows). For weekly/monthly intervals, move the bucketing into SQL with `TruncWeek`/`TruncMonth` per `StatisticIntervalChoices` and return an annotation directly.

- [ ] **Dashboard/render N+1** — `django_spire/metric/visual/signage/services/transformation_service.py:46-71` — *confirmed, and the live loop is real*
  - `display_slides` does per-presentation `slides.filter`, per-slide `sections.select_related('visual').prefetch_related('visual__conditions')`, then **per-section `render_context()` → `current_value()` → an aggregate query** (`visual/services/transformation_service.py:222-240`); chart sections add `series_datasets()` → one aggregate per dataset (:131-153); `series_breakdown`/`dataset_values`/`gauge_max` query again. A 10-slide × 4-section board ≈ 40+ aggregate queries per full render.
  - Nothing is cached; the live loop is client-side but server-hitting: `chart.html:43-64` polls `Glue.function` on a timer — `chart_update_interval` defaults to **3s** on the signage kiosk (`display_page.html:117` doesn't forward the view's 15s), live regions use `VISUAL_REGION_LIVE_UPDATE_INTERVAL = 10` (`visual/constants.py:3`). Each poll re-runs `build_option_body` (`visual/charts.py:17-27`) → fresh aggregates.
  - **Suggested fix**
    - Collapse per-section rows into one query: fetch the whole slide set's statistics, then run a single `StatisticValue` aggregation over the shared date-range grouped by `statistic` + day (and `reference` for datasets), and drive `render_context()` from that in-memory dict instead of per-section `current_value()` queries.
    - Cache the aggregated render result (Django cache, keyed on `visual.pk + as-of date + statistic updated_at`), with a TTL ≤ the poll interval, so `N` charts × clients don't multiply DB load.
    - Fix `display_page.html` to forward `chart_update_interval` (or drop the confusing context value) so the kiosk honors the intended 15s, not the 3s default.

- [ ] **`ReportRun` grows forever with no index** — `django_spire/metric/report/models.py:7-19` — *confirmed*
  - One row per executed report (`report/views/page_views.py:140`), plain model, `TextField report_key_stack` + `datetime` with **no index and no retention**; `by_top_ten`/`run_count` (`report/querysets.py:7-18`) are full-table GROUP BY / COUNT scans.
  - **Suggested fix**
    - Add `db_index=True` on `datetime` (used for retention + ordering) and prune runs older than a configured window in a scheduled task.
    - For "popular report" counts, add a btree index on a normalized `report_key` FK to a small `Report` catalog table (best), or a `pg_trgm`/`varchar_pattern_ops` index on `report_key_stack` (see the `TextField` item under Minor). Then `by_popular`/`run_count` become index scans.

- [ ] **Soft-delete cascades are non-atomic + N+1, and `Domain.set_deleted()` stops halfway** — `django_spire/metric/domain/models.py:27-31` — *confirmed*
  - `Domain.set_deleted()` iterates subdomains (one query each, no `transaction.atomic()` — a mid-loop crash leaves partial deletion) and **never touches `statistic_groups` / `statistics` / `values`** (`statistic/models.py:51-53` only cascades `StatisticGroup → statistics`; `Statistic` inherits `HistoryModelMixin.set_deleted` and only soft-deletes itself). A deleted domain's metrics stay active and keep rendering.
  - Two inconsistent cascade styles: `StatisticGroup`/`Presentation`/`Slide` (`presentation/models.py:26-28, 49-51`) bulk-`update(is_deleted=True)` children (activity rows covered by bulk signals, but **`HistoryEvent` rows are skipped**), while `Domain` iterates per-row (writes history events). Views drive these at `domain/views/form_views.py:53`, `statistic/views/form_views.py:45, 89`.
  - **Suggested fix**
    - Unify on one style: wrap the entire cascade in `transaction.atomic()`; for the child bulk-updates, walk the affected PKs and write `HistoryEvent`s in one batch (the pattern the bulk signals already use for activity) so history is consistent.
    - Complete the cascade in `Domain.set_deleted()`: `statistic_groups.update(is_deleted=True)` → for each group's `statistics` → soft-delete statistics → mark values unreachable. Because `StatisticValue` has no soft-delete field, either (a) make it a `HistoryModel`/add `is_deleted` in a forward migration, or (b) hard-delete its values when the parent statistic is soft-deleted (acceptable for raw metrics), or (c) filter by the statistic's deleted state at read time (preferred — see the "soft-deleted statistic still renders" item, which this makes consistent).

- [ ] **Signage M2M soft-delete fragility** — `django_spire/metric/visual/signage/models.py:39-43` — *confirmed as a latent trap, not an active bug*
  - `Signage.set_deleted()` soft-deletes through rows, but the raw `signage.presentations` M2M **does not filter `is_deleted`**. The render path is safe (`presentations()` in `signage/services/transformation_service.py:35-44` filters through-row + presentation; views/templates use `presentation_links()` — no template touches the raw M2M). The **only** unfiltered consumer is the test `signage/tests/test_models.py:68`, which asserts the raw M2M.
  - **Suggested fix**
    - Give `SignagePresentationQuerySet` (signage/querysets.py:37) a default `get_queryset()` that filters `is_deleted=False` and set it as the through model's manager, so the M2M accessor excludes soft-deleted links by default. Then update the test (and the `for_signage`/`with_presentation` helpers) to match and to assert that deleted through-rows no longer surface.
    - If a default-filter is undesirable (some path needs deleted links), instead centralize on `SignageTransformationService.presentations()`/`presentation_links()` and add a documented comment + a lint/test guard so no future consumer reaches for the unfiltered M2M.

## Migration problems / future-migration traps

- [ ] **The `0002` data migration scales badly for consumers** — `domain/migrations/0002_statisticvalue_sub_domain.py:15-29` — *confirmed*
  - `list(StatisticValue.objects.all())` (whole table in RAM), per-row `row.statistic` FK loads (N+1), then `bulk_update`; and it silently reassigns `sub_domain` to an arbitrary sub-domain (`filter(...).first()`, fallback `objects.first()`) when NULL — data attribution loss. Already shipped, so it can't be rewritten.
  - **Suggested fix**
    - For any currently-un-migrated consumer on the pre-0002 schema: apply the fix as a follow-up before shipping, or backfill the correction externally (re-run normalization in `iterate_in_batches` with explicit PK batching and a deterministic `sub_domain` selection). Going forward, replace the `list(...all())` pattern in new data migrations with `iterator(chunk_size=...)` or PK-batch loops, and never assign data-attribution columns to an arbitrary row.

- [ ] **`0003_subdomain_key` backfills one shared uuid, so the null-filtered `fill_keys` no-ops and the unique index build fails on data-bearing installs** — `domain/migrations/0003_subdomain_key.py:24-34` — *confirmed (precision: ≥2 rows, failure at the inline UNIQUE)*
  - Verified against Django's schema editor: `AddField('key', default=uuid4, null=True, unique=True)` renders the Python-evaluated constant inside `ALTER TABLE ... ADD COLUMN "key" uuid NULL DEFAULT '<uuid>' UNIQUE` (Django evaluates `field.get_default()` **once** and includes it because `skip_default_on_alter` is False for Postgres, even for a nullable field). On existing rows PG materializes that **same constant** (fast default), so `fill_keys` (`key__isnull=True`) updates nothing, and the inline `UNIQUE` at the AddField step fails on any install with **≥2** existing `SubDomain` rows (a single row still succeeds). It only "worked" because the DB was fresh/empty.
  - **Suggested fix**
    - Correct pattern (for any rewrites/forward fixes): `AddField('key', fields.UUIDField(null=True, editable=False))` (no default) → `RunPython(fill_keys)` filling `isnull` rows **unconditionally** (or per-PK batch) → `AlterField` to `unique=True, null=False`. If consumers on existing data must keep `0001`→`0008`, ship a forward/squash migration that does the same repair (add nullable, backfill, enforce) so upgraded installs converge. Add a comment on `0003` flagging the trap.

- [ ] **Migration history rewrite leftovers** — `domain/migrations/__pycache__/` — *confirmed but purely cosmetic*
  - Stale `.pyc`s for migrations that no longer exist: `0002_remove_domain_key_domain_description_and_more`, `0003_alter_subdomain_options`, `0004_statisticgroup_statistic_statisticvalue`, `0004_trackinglink`, `0005_alter_statistic_group` (their `0004`/`0005` names collide with the current `0004_alter_statistic_key_alter_subdomain_key`/`0005_statistic_value_type` — proof of a rename/squash without a clean). Orphaned `.pyc`s are inert at runtime.
  - **Suggested fix**
    - Add `makemigrations --check --dry-run` (or `--check`) to CI/prerelease so a rename/squash that leaves divergent files (or missing model changes) fails the build.
    - Ignore migration `__pycache__/` in `.gitignore` (`**/migrations/__pycache__/`) and delete the stale files once, so anyone diffing migration history sees only real migrations.

## Traps / gotchas

- [ ] **`add_value` quantizes after save — dead code + missing input guard** — `django_spire/metric/domain/statistic/services/processor_service.py:49-52` — *confirmed*
  - `values.create(...)` persists the row, then `statistic_value.value = statistic_value.value.quantize(...)` mutates only the in-memory object, which is never saved; PG `numeric(16,4)` rounds on insert anyway (round-half-away vs quantize's `ROUND_HALF_EVEN` — edge divergence). Separately, `record_value`'s `StatisticValueIn.reference` (`api_v1.py:20`) has no `max_length`.
  - **Suggested fix**
    - Delete the dead `quantize` line (or quantize the `Decimal` **before** `create()` if exact rounding semantics are wanted — pick one documented rounding mode and apply it consistently).
    - Add `max_length=255` to `StatisticValueIn.reference` so >255-char input 422s instead of surfacing a PG `DataError` as a 500.

- [ ] **Soft-deleted `statistic` still renders live aggregates** — `django_spire/metric/visual/models.py:47-49`, `django_spire/metric/domain/statistic/services/transformation_service.py:35-42` — *confirmed full-stack: no layer checks it*
  - `Visual.statistic` FKs with `on_delete=SET_NULL` (hard delete only); the render path — `current_value`/`series_datasets`/`series_breakdown`/`dataset_values`/`gauge_max` (`visual/services/transformation_service.py:65-210`) — queries `self.obj.statistic.values` with **no `is_deleted` filter**; `render_context` checks only `visual.is_deleted` (:222-240); the region tag (`templatetags/django_spire_metric_region.py:28`) checks `visual` only; templates render `visual.statistic`/`current_value` unconditionally.
  - **Suggested fix**
    - Filter deleted statistics at the transformation layer, once: in `StatisticTransformationService.value_queryset` (and the `VisualRegion`/chart paths), bail out (return `0`/empty context) when `self.obj.is_deleted` — or add a `not_deleted()` filter on the statistic relation in `current_value`/`series_*`/`breakdown`/`gauge_max`/`dataset_values`.
    - Also guard `render_context`/`render_visual_region` to render the "No data"/empty state when `visual.statistic_id` points at a deleted statistic, so the charts and kiosk show a clean empty instead of stale numbers. This dovetails with the cascade fix (marking values unreachable when a side is deleted).

- [ ] **`SlideSection` lacks uniqueness on `(slide, row, col)`** — `django_spire/metric/visual/presentation/models.py:89-92` — *confirmed*
  - `Slide` (:58-62), `VisualCondition` (:247-251), `VisualReference` (:274-278), `SignagePresentation` (:77-80) all get order/loc unique constraints; `SlideSection` does not — two sections can silently occupy the same grid cell (it only sets `ordering = ('row', 'col')`).
  - **Suggested fix**
    - Add `models.UniqueConstraint(fields=('slide', 'row', 'col'), name='unique_slide_section_cell')` (and the related migration). Handle the pre-existing-duplicates case in the migration (dedupe/reassign `row`/`col`) or in a data-migration before adding the constraint.

- [ ] **Permission catalog is incomplete for the group-permission UI** — `django_spire/metric/domain/apps.py:17`, `visual/apps.py:14`, `presentation/apps.py:14`, `signage/apps.py:14` — *confirmed (scope: grant/UI gap, not enforcement)*
  - `MODEL_PERMISSIONS` lists only `Domain` + `Statistic` (missing `SubDomain`, `StatisticGroup`, `StatisticValue`); visual only `Visual` + `VisualRegion` (missing `VisualCondition`, `VisualReference`); presentation only `Presentation` (missing `Slide`, `SlideSection`); signage only `Signage` (missing `SignagePresentation`); report only `ReportRun` (fine). CRUD views require the missing codenames (`view_subdomain`/`delete_subdomain` at `domain/views/page_views.py:53`, `form_views.py:111`; `add/change/delete_statisticgroup|statistic` at `statistic/views/form_views.py:25-79`; `add/change/delete|view_slide|slidesection` at `presentation/views/form_views.py:96-218`; `add/change/delete_signagepresentation` at `signage/views/form_views.py:99-139`).
  - Scope nuance: `generate_model_permissions` (`auth/permissions/tools.py:19`) drives the **group-permission management UI** and `generate_user_perm_data`, so these models can't be granted/configured there — but Django auto-creates the underlying DB permissions, `permission_required` enforces them, and `django_spire/metric/auth/controller.py:3-23` already enumerates the full view-permission set (incl. proxies) for its `can_*` methods. Enforcement works; the gap is the grant catalog.
  - **Suggested fix**
    - Regenerate `MODEL_PERMISSIONS` per `apps.py` to cover every **concrete** model: domain → `Domain`, `SubDomain`, `StatisticGroup`, `Statistic`, `StatisticValue`; visual → `Visual`, `VisualCondition`, `VisualReference`, `VisualRegion`; presentation → `Presentation`, `Slide`, `SlideSection`; signage → `Signage`, `SignagePresentation`. Leave the 5 proxies out (they share the concrete `Visual` permission) but keep `metric/auth/controller.py` as the source of the view-permission list templates rely on. Regenerate the migration that seeds permissions if `MODEL_PERMISSIONS` feeds one.

## Minor / consistency

- [ ] **MRO order inconsistent with convention** — models declare `HistoryModelMixin, ActivityMixin` (`domain/models.py:16,39`, `statistic/models.py:29,59`); documented convention is `ActivityMixin, HistoryModelMixin`. Verified: the two mixins' method sets don't overlap (`HistoryModelMixin`: `save`/`set_active`/`set_deleted`/`set_inactive`/`un_set_deleted`, `history/mixins.py:26-66`; `ActivityMixin`: `add_activity` + `creator`, `history/activity/mixins.py:20-48`), so there is **zero functional impact** — purely cosmetic.
  - **Suggested fix**
    - Flip the base-class order on the 4 metric models to `ActivityMixin, HistoryModelMixin` (pure reorder, no behavior change, no migration) to match the house convention.

- [ ] **`report_key_stack` as `TextField`** — `report/models.py:8` — blocks btree-indexed "popular report" counts; a trigram index or a normalized parent table is the fix (see the `ReportRun` scaling item above).
  - **Suggested fix**
    - Normalize `report_key` into a small `Report` catalog table (FK from `ReportRun`, btree-indexed) and make `by_popular`/`run_count` group on the FK; or, if keeping the denormalized stack, add a `pg_trgm` GIN index (or `varchar_pattern_ops` btree) on `report_key_stack` so the GROUP BY / COUNT scans become index-backed.

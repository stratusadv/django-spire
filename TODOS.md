# TODOs — `django_spire.metric` Review

---

## Completed

- [x] **`interval_summary` aggregates in Python** — `django_spire/metric/domain/statistic/services/transformation_service.py` is now SQL-native: `TruncDate` day-group + `Sum`/`Count` in SQL, reduced to interval buckets in Python (memory O(days), not O(rows)). Weekly stays Sunday-based (`TruncWeek` would shift buckets); percentage stays per-row weighted.
- [x] **Dashboard/render N+1** — `display_slides` builds the board from the prefetched tree (`presentations().with_slides()`, ~4 queries total, no per-node selects; deleted-visual sections filtered in Python). Kiosk now forwards `chart_update_interval` (15s, not 3s). `current_value`/`series_datasets`/`series_breakdown`/`dataset_values`/`gauge_max` cached in `VisualTransformationService` (Django cache, revision-keyed on `Max(timestamp)`, TTL 120s).
- [x] **Soft-delete cascades are non-atomic + N+1, and `Domain.set_deleted()` stops halfway** — new `django_spire/history/utils.py::soft_delete_queryset` bulk-flips children and backfills one `HistoryEvent(DELETED)` per row; every cascade wrapped in `transaction.atomic()`; `Domain` now reaches groups → statistics, `Presentation` reaches sections; `StatisticGroup`/`Slide`/`Signage` unified on the same helper.
- [x] **Soft-deleted `statistic` still renders live aggregates** (trap) — read-time filter (option c): `StatisticTransformationService.value_queryset` returns `none()` for deleted stats (totals/summaries → 0/`{}`), visual aggregates return `0`/`[]`, `render_context` returns the empty state. No `StatisticValue` schema change.

## Scaling

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

- [ ] **`add_value` quantizes after save — dead code** — `django_spire/metric/domain/statistic/services/processor_service.py:49-52` — *confirmed*
  - `values.create(...)` persists the row, then `statistic_value.value = statistic_value.value.quantize(...)` mutates only the in-memory object, which is never saved; PG `numeric(16,4)` rounds on insert anyway (round-half-away vs quantize's `ROUND_HALF_EVEN` — edge divergence). (The `max_length=255` input guard on `StatisticValueIn.reference` was added already — oversized references now surface a `ServiceError`.)
  - **Suggested fix**
    - Delete the dead `quantize` line (or quantize the `Decimal` **before** `create()` if exact rounding semantics are wanted — pick one documented rounding mode and apply it consistently).

- [ ] **`SlideSection` lacks uniqueness on `(slide, row, col)`** — `django_spire/metric/visual/presentation/models.py:89-92` — *confirmed*
  - `Slide` (:58-62), `VisualCondition` (:247-251), `VisualReference` (:274-278), `SignagePresentation` (:77-80) all get order/loc unique constraints; `SlideSection` does not — two sections can silently occupy the same grid cell (it only sets `ordering = ('row', 'col')`).
  - **Suggested fix**
    - Add `models.UniqueConstraint(fields=('slide', 'row', 'col'), name='unique_slide_section_cell')` (and the related migration). Handle the pre-existing-duplicates case in the migration (dedupe/reassign `row`/`col`) or in a data-migration before adding the constraint.



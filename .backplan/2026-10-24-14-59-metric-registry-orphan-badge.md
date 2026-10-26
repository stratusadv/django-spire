# Metric registry orphan flag + badge

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-24-14-59

## End State

`Domain`, `SubDomain`, `StatisticGroup`, and `Statistic` each carry an `is_orphaned` BooleanField (default `False`); every `metric_build` (build mode only) sets it `True` on rows whose key is in no configured registry and clears it `False` on rows that are; and a warning badge with a native `title` hover hint (Bootstrap tooltip JS explicitly deferred, user decision) is shown on every metric list row, detail card, statistics/storage table row, and form page when (and only when) the object is orphaned.

## Observable Concern

The three Alpine list rows each depend on `item.is_orphaned` being present in their Glue payload: the domain and subdomain lists use `fields='__all__'` (automatic), but `group_list_view` uses an explicit `Glue.fields(...)` selection that must gain `is_orphaned` or the group-list badge silently never renders. Completion test 3 asserts each surface's markup, which pins this.

## Current State

Verified facts:

- **Command**: `django_spire/metric/domain/management/commands/metric_build.py` — `handle()` calls `_print_orphans(registries)` in build mode only (never in `--check`). `_print_orphans` builds `declared: dict[str, set[str]]` from `registry.stored_keys()` (keys `domains`/`subdomains`/`statistic_groups`/`statistics`), then walks `Model.objects.active().not_deleted()` per level and prints `orphan (not in any registry): ...` WARNING lines. It never writes to the DB.
- **Models** (all `HistoryModelMixin, ActivityMixin`, all in app `django_spire_metric_domain`):
  - `Domain`, `SubDomain` in `django_spire/metric/domain/models.py`; `StatisticGroup`, `Statistic` in `django_spire/metric/domain/statistic/models.py`.
  - Every model's `.key` SlugField stores the *stored* (composite) key that `stored_keys()` produces, so `key in declared[level]` is the exact membership test the printer already uses.
  - `HistoryModelMixin.is_active`/`is_deleted` are `editable=False`; the same treatment fits `is_orphaned`.
- **Migrations**: latest is `django_spire/metric/domain/migrations/0010_domain_key_statisticgroup_key.py`; all four models share that one migrations package.
- **Pages/templates** (badge surfaces; "core" = list rows + detail cards + tables, all user-confirmed, plus user-confirmed extras):
  - Domain list rows: `metric/domain/scroll/scroll.html` (Alpine `x-for` item; `list_view` uses `Glue.queryset(..., fields='__all__')`, so the new field flows through automatically).
  - Domain detail card: `metric/domain/card/detail_card.html` (server-side `domain`).
  - SubDomain list rows: `metric/domain/scroll/subdomain_scroll.html` (Alpine item; `detail_view` uses `fields='__all__'`).
  - SubDomain detail card: `metric/domain/card/subdomain_detail_card.html` (server-side `subdomain`).
  - Group list rows: `metric/domain/statistic/scroll/group_scroll.html` (Alpine item; **`group_list_view` uses an explicit `Glue.fields(...)` list — `is_orphaned` must be added there**).
  - Group detail card: `metric/domain/statistic/card/group_detail_card.html` (server-side `group`).
  - Statistic rows: `metric/domain/statistic/card/group_statistics_card.html` (server-side `statistics`; rendered on both group detail and sub-domain detail pages), plus `metric/domain/statistic/card/storage_card.html` (storage page table; user-confirmed extra).
  - Statistic detail card: `metric/domain/statistic/card/detail_card.html` (server-side `statistic`).
  - Form pages (user-confirmed extra): `page/form_page.html`, `page/subdomain_form_page.html`, `statistic/page/group_form_page.html`, `statistic/page/statistic_form_page.html` — the four form views (`domain/views/form_views.py`, `statistic/views/form_views.py` `_group_form_view`/`_form_view`) currently do **not** put the object in context; it must be added (only meaningful for saved instances).
- **Admin**: only `Domain` and `SubDomain` are registered (`django_spire/metric/domain/admin.py`, `list_display`/`readonly_fields` follow a fixed pattern); no admin exists for `StatisticGroup`/`Statistic`.
- **Tooltip infra**: Bootstrap 5.3 bundle JS is loaded globally in `base.html`; no tooltip init exists in Spire JS; house JS pattern is `document.addEventListener('alpine:init', ...)`; the one existing usage is `comment_item.html` (`data-bs-toggle="tooltip" data-bs-placement="top" title="..."`), which is inert today.
- **Seeders**: `DomainSeeder`, `SubDomainSeeder` (`metric/domain/seeding/seeder.py`) and `StatisticGroupSeeder`, `StatisticSeeder` (`metric/domain/statistic/seeding/seeder.py`) use explicit `fields_seeds` dicts that name `is_active`/`is_deleted` with `Seeder.static(...)`; a new field needs the same explicit entry.
- **Tests**: `django_spire/metric/domain/tests/test_management.py` (`MetricBuildCommandTestCase.test_build_lists_orphans` pins the `orphan (not in any registry):` output line), `tests/test_views/test_page_views.py` (asserts on `response.content` + `response.context`), factories in `tests/factories.py` and `statistic/tests/factories.py`.
- **House style**: list rows use `attribute-label` + column layout; badges are plain Bootstrap; docs for the registry live in `docs/app_guides/metric/registry.md`.

## Plan

1. Add `is_orphaned` to the four models + migration
   - `is_orphaned = models.BooleanField(default=False, editable=False)` on `Domain`, `SubDomain`, `StatisticGroup`, `Statistic` (placed after `description`, before `objects`).
   - Generate `0011` in `django_spire/metric/domain/migrations/` with `just make-migrations`; apply with `just migrate`.
   - Done when the new migration contains exactly four `AddField` operations for `is_orphaned`, applies cleanly, and `python manage.py makemigrations --check` is silent.

2. Make `metric_build` set/clear the flag idempotently (build mode only)
   - In `metric_build.py`, extend the orphan pass (rename `_print_orphans` → `_apply_orphans` or similar): keep the existing per-orphan WARNING lines, and for each of the four models run two queryset updates over `.active().not_deleted()` — `filter(is_orphaned=False).exclude(key__in=keys).update(is_orphaned=True)` and `filter(is_orphaned=True).filter(key__in=keys).update(is_orphaned=False)` — plus one summary line (e.g. `orphan flag: flagged N, cleared M`). Queryset `.update()` is used deliberately: no `save()` overhead, no activity-signal noise. `--check` mode stays read-only (user-confirmed).
   - Done when new `test_management.py` tests pass: a stray row is flagged after build; a row is cleared when its key is re-registered (idempotent); `--check` performs no flag writes; soft-deleted rows are never touched; the existing `orphan (not in any registry):` output still appears.

3. ~~Tooltip support in Spire JS (fallback: drop and rely on native `title`)~~ — **skipped by user decision (2026-10-24): no JS change; the badge uses the native `title` attribute only and carries no `data-bs-toggle="tooltip"`.**
   - ~~In `django_spire/core/static/django_spire/js/ui.js`, add a delegated handler: on `mouseover`, `event.target.closest('[data-bs-toggle="tooltip"]')`; if found and not yet initialized (guard with a `dataset` flag), `new bootstrap.Tooltip(el)`. Bootstrap strips the native `title` on init, so no double tooltips; this also activates the existing comment tooltip.~~
   - ~~Done when the handler is in `ui.js` and reads correctly against the Bootstrap 5.3 API (no automated JS test exists in this repo; verified by inspection and, if available, a quick browser smoke of a metric list page).~~

4. Badge partial template
   - New `django_spire/metric/domain/templates/django_spire/metric/domain/orphan_badge.html`: renders nothing unless the passed flag is true; otherwise a warning badge (`badge text-bg-warning` with `bi-exclamation-triangle` + "Orphaned") carrying a native `title` hover hint ("Not present in any configured Metric registry as of the last metric_build run."). No `data-bs-toggle="tooltip"` (tooltip JS deferred).
   - Done when included with `with is_orphaned=True` it renders the badge markup and with `False`/unset it renders an empty string.

5. Place the badge on all confirmed surfaces
   - Alpine list rows (domain `scroll/scroll.html`, subdomain `subdomain_scroll.html`, group `group_scroll.html`): badge inside the name cell with `x-show="item.is_orphaned"`.
   - `group_list_view`: add `is_orphaned` to the explicit `Glue.fields(...)` selection.
   - Detail cards (domain, subdomain, group, statistic): include the partial as the first element of the card body, driven by `{% if obj.is_orphaned %}`.
   - Tables: `group_statistics_card.html` and `storage_card.html` rows — badge next to the statistic name link.
   - Form pages: add the instance to context in the four form views (only when the instance has a `pk`) and include the partial at the top of each of the four form page templates.
   - Done when every listed template contains the include, the group Glue selection includes `is_orphaned`, and the form views pass the object.

6. Django admin (Domain + SubDomain only, the only registered admins)
   - Add `is_orphaned` to `list_display` and `readonly_fields` in both admins, following the existing `is_active`/`is_deleted` pattern.
   - Done when the admin change list renders the column and the change form shows it read-only.

7. Seeders
   - Add `'is_orphaned': Seeder.static(False)` to all four metric seeders (matches the explicit `is_active`/`is_deleted` entries).
   - Done when `just test-app django_spire/metric` (incl. seeding tests) and the seeding suite pass.

8. Tests for the badge surfaces
   - Page-view tests: detail cards and tables are server-rendered, so assert the badge markup (e.g. the `Orphaned` badge span + its `title` hint) appears when `is_orphaned=True` and is absent otherwise for domain detail, subdomain detail, group detail, statistic detail, group list (Alpine row → assert the partial markup with `x-show="item.is_orphaned"` is in the HTML), storage page, and the statistics tables.
   - Form-view tests: update view shows the badge for an orphaned instance, create view shows nothing.
   - Done when the new tests pass and the metric suite is green.

9. Docs
   - `docs/app_guides/metric/registry.md`: document the `is_orphaned` field, that `metric_build` (build mode) sets/clears it idempotently, and the badge/tooltip on the UI.
   - Done when the doc describes the field, the command behavior, and the badge; `just docs-tests` still builds.

10. Verify
   - `just python -m pytest django_spire/metric --reuse-db -n 12 -q`, the seeding suite, and `just test` for the full suite; `.venv/bin/ruff format --check` + `ruff check` on every touched file; pre-commit simulation over the staged set.
   - Done when all of the above pass with no new errors and the pre-existing 19 `core/components` failures are the only failures.

## Completion Test

1. `just python -m pytest django_spire/metric --reuse-db -n 12 -q` → all pass, including the new orphan-flag command tests and badge view tests.
2. Fresh-DB script via `just python`: create a stray `Domain` (key not in any registry), run `call_command('metric_build')`, assert `domain.is_orphaned is True`; register the key (or run against a registry containing it), run again, assert `False`; run `metric_build --check` after re-orphaning and assert the flag did not change.
3. GET the domain list/detail, subdomain detail, group list/detail, statistic detail, storage, and a form page with an orphaned row: each response contains the warning badge markup with its native `title` hint; with a registered row: it does not.
4. `.venv/bin/ruff format --check` and `.venv/bin/ruff check` clean on all touched files; `just test` shows no new failures beyond the known 19 `core/components` ones.

## Observed Results (2026-10-24)

1. `just python -m pytest django_spire/metric --reuse-db -n 12 -q` → `671 passed, 1 warning in 10.75s` (was 658 before the new tests; includes the 4 `MetricBuildOrphanFlagTestCase` tests and the 9 badge view/form tests).
2. Covered by `MetricBuildOrphanFlagTestCase`: `test_build_flags_orphaned_rows` (all four levels flagged), `test_build_clears_flag_for_registered_rows` (key `store` re-registered → cleared), `test_check_does_not_update_flag` (`--check` leaves the flag untouched in both directions), `test_build_ignores_soft_deleted_rows`.
3. Covered by `OrphanBadgeViewTestCase` + `OrphanBadgeFormViewTestCase`: badge title present/absent per state on domain detail (count 1→2, baseline is the Alpine row), subdomain detail (0→2: card + statistics table), group detail (0→2), statistic detail (0→1), storage (0→1), group/domain list row markup (`x-show="item.is_orphaned"`), update form shows the badge, create form does not.
4. `.venv/bin/ruff format` + `.venv/bin/ruff check` clean on all touched files (touched files reformatted to the 120-col setting); pre-commit simulation (`ruff check` over the full staged `.py` set) → `All checks passed!`; `just test` → `4798 passed, 19 failed` (the 19 are the pre-existing `core/components` `Glue.child` shim failures, unchanged); `just docs-tests` → `Documentation built in 48.59 seconds`; `manage.py makemigrations` → `No changes detected`.

## Deviations

1. Tooltip JS skipped
    - What: step 3 (delegated Bootstrap tooltip init in `ui.js`) is struck through; the badge carries only a native `title` attribute and no `data-bs-toggle="tooltip"`.
    - Why: user decision (2026-10-24) to skip the tooltip for now; the native `title` still provides the hover hint with zero JS, and the markup stays compatible with a future Bootstrap-tooltip init.
2. Multi-line `{% include %}` tags collapsed to one line
    - What: the `orphan_badge.html` includes in the subdomain/group/statistic detail cards, the two tables, and three form pages were initially written as two-line `{% include ... with ... %}` tags; all are now single-line.
    - Why: Django's template lexer only matches tags within a single line — a line-broken include renders as literal template text in the HTML (confirmed by the four failing badge view tests and an `engines['django'].from_string` experiment). The single-line includes in `card/detail_card.html` and `page/form_page.html` had already worked, which isolated the difference.

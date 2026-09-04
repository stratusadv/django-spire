# Changelog

## v1.0.1 - September 3, 2026

### Fixes

- Updated API security logic to match forms & display.
- Fixed Auth User page from displaying 2 dispatch modals.
- A required `select_widget.html` field with no placeholder no longer looks filled in while actually submitting empty.
- Glue scroll lists (`glue/scroll/scroll.html`) now bust their cached query results on reset, so a row removed or filtered out elsewhere (e.g. by a delete, or an edit that changes which list it belongs in) no longer reappears from stale cached data.

## v1.0.0 - September 2, 2026

### Overview

First stable release of the v1 line. Everything the 0.x series shipped is here (last
release: v0.32.11), rebuilt on Django 6, `django-glue` v1.0.0, and Python 3.12. v1 adds
four new framework apps (API, Celery, file, metric), a rewritten seeding system, a
service layer, an event-based activity/audit trail, a global search palette, and an
overhauled admin, navigation, and front-end stack.

### Breaking

- Migrated from `django-glue` v0.8.x to `django-glue` v1.0.0. Every glue-enabled
  template, view, and client call uses the new attribute/widget syntax; `js_url` was
  renamed to `glue_url` and moved onto the `Glue` client global.
- Minimum Python raised to 3.12; test project restructured from a flat layout to an
  app-based layout (`test_project/app/`).
- `ApiAccessLevelChoices` replaced by `ApiPermissionChoices` (level → permission), with
  granular view/add/change/delete API permissions.
- `django_spire.sync` removed (synchronization functionality dropped) and
  `django_spire.contrib.sync` with it.
- `django_spire.changelog` app removed, replaced by the `render_markdown` template tag.
- Profiling middleware removed; `django_spire.theme` app removed (theming now lives in
  `core` SCSS variables + `theme.js`).
- Seeding rewritten: `cache_enabled` removed, seeder API and configuration changed, old
  seeders must be migrated to the new field-seeder types.
- Per-app view-level auth controllers (`django_spire.auth.controller`,
  `help_desk/auth/controller.py`, etc.) removed. Use the `permission_required` decorator
  (`django_spire.auth.permissions`) instead.
- `spire_opencode` management command and bundled agent/skill files no longer ship in the
  package.
- Legacy `django_spire.core` modules relocated to the package root (`constants.py`,
  `conf.py`, `exceptions.py`, `settings.py`, `shortcuts.py`, `tools.py`, `urls.py`);
  `contrib.breadcrumb` replaced by `contrib.navigation`.
- App URL patterns are auto-discovered through `URLPATTERNS_INCLUDE` +
  `URLPATTERNS_NAMESPACE`; apps now split URL config into `urls/page_urls.py` and
  `urls/form_urls.py`.
- `distinct` query handling removed from scroll/querysets.
- Contrib helpers consolidated: `pagination`, `progress`, `performance`, `gamification`,
  `html_renderer`, `generic_views`, `help`, `choices`, and `service` were removed or
  merged into `responses`, `form`, `ordering`, and `constructor`.
- New installs must add `django_spire.history.activity.middleware.ActivityUserMiddleware`
  to `MIDDLEWARE` after `AuthenticationMiddleware` (system checks `W001`–`W003` flag it).
- `Site` object now reads `DJANGO_SITE_NAME`/`DJANGO_SITE_DOMAIN` instead of a fixed host.
- `Domain.set_delete()` overridden so deleting a domain cascades through sub-domains,
  statistic groups, and statistics.

### Features

- **`django_spire.api`** — REST API backend (django-ninja, mounted at `api/v1/`) with
  hashed API-key authentication, granular permission levels, and an access management UI.
- **`django_spire.celery`** — Celery task queue support: task manager, progress tracking,
  results, toast/detail UI, and infinite-loop detection and prevention.
- **`django_spire.file`** — generic file management: uploader/handler, extensions,
  temporary media, AJAX upload endpoints, admin, and seeding.
- **`django_spire.metric`** — metrics system:
  - `domain` — domain/sub-domain CRUD, admin panels, infinite scrolling, auto-slugged
    sub-domain keys, and seeding.
  - `statistic` — statistics grouped under a domain with daily/weekly/monthly intervals
    and number/percentage/currency values; `StatisticValue` rows per reference, indexed
    for interval/reference lookups; page-view and click tracking via
    `StatisticClickMiddleware` written by a background queue; a REST API
    (`metric/domain/statistic`) to record and read values; aggregations, retention
    pruning (`prune_metric_statistic_values`), and tracking caps.
  - `visual` — indicator, line, bar, area, pie, and gauge ECharts; threshold conditions
    with state colors and tolerance; references for dataset series; named, optionally
    live-updating visual regions rendered anywhere via `render_visual_region`.
  - `presentation` — slide-based presentations with grid-positioned sections.
  - `signage` — signage displays with ordered presentation links and a public display view.
  - `report` — report registry and rendering with sub-navigation and a print view.
- **`django_spire.contrib.rest`** — queryset-like access layer for external REST sources:
  schema/schema-set architecture, bearer auth, pagination, and prefetch support.
- **`django_spire.contrib.converters`** — convert Django models to Pydantic classes,
  data dicts, and enums.
- **`django_spire.contrib.navigation`** — navigation/breadcrumb model extracted from the
  old breadcrumb module.
- **`django_spire.contrib.chart`** — ECharts helpers for visual components.
- **Activity & audit trail** (`django_spire.history.activity`) — event-based activity
  records: automatic `created`/`updated`/`deleted` on save and soft-delete, bulk
  activities for `bulk_create`/`bulk_update`/`update`/`delete`, m2m `added`/`removed`
  activities, request-user attribution via `ActivityUserMiddleware`, and
  `activity_user()` for off-request work (Celery tasks, management commands).
- **Search palette** (`django_spire.core.search`) — Ctrl/Cmd-K global search across
  registered models and commands via a `Search` subclass registry
  (`DJANGO_SPIRE_SEARCH_REGISTRY`), with per-model searchable fields, commands, and
  permissions.
- **Seeding system overhaul** — new field seeder types (callable, custom, exclude, file,
  index, mutate, model with ordered/random foreign keys, LLM, static), seeding meta,
  init/mutate seed logic, multi-FK support, and optional faker/LLM data.
- **Infinite scrolling** — `GlueScroll` for task, domain, sub-domain, statistic, and
  notification lists with customizable scroll increments and ordering/filtering overrides.
- **Task app** — infinite nested tasks, rich task cards, task duplication, interactive
  status updates, and child lists.
- **Auth** — password change enforcement on first login, email lowercase normalization,
  user and group management pages with permission matrices, MFA page, SMS verification
  (`auth/sms`) with `DJANGO_SPIRE_AUTH_SMS_*` settings, and full password reset flows.
- **Glue widgets** — required-field red asterisks, `field-input`/`field-change`/
  `field-focus`/`field-blur` events, search-and-select and multi-search widgets, decimal
  precision, and multi-file upload support.
- **Markdown rendering** — `render_markdown` template tag with code blocks, fenced-code
  rendering, and Editor.js support, replacing the changelog app.
- **Front-end** — button loading states, slide button component, brand logo, `.woff2`
  fonts, consolidated SCSS with theme CSS variables, tightened navigation with responsive
  icons and FOUC prevention, and `preconnect`/`defer` for first-load performance.
- **Knowledge** — entity admin panels, collection navigation and reordering, entry import,
  version editor and publish flow, code blocks, SMS integration with webhook handling and
  `KnowledgeSearchRouter` intent routing, and a search-index rebuild command.
- **Help desk** — full CRUD refactor with action buttons, sorting, breadcrumbs, and a
  services layer.
- **Comment / notification / file / REST client** — CRUD pages, breadcrumbs, app
  notification list/dropdown, and AJAX endpoints.
- **Admin** — `SpireModelAdmin` (`model_class` self-configuration, auto `list_display`
  and `search_fields` that exclude secret fields, `list_select_related` population),
  admin link helpers (`admin_change_link`, `external_link`, ...), query-count guarded
  admin tests, and a Playwright walkthrough of every changelist and change form.
- **Tooling** — `spire_startapp` (interactive app generator), `spire_flush`,
  `spire_remove_migration`, `spire_compile_scss`, `prune_metric_statistic_values`, and
  `rebuild_knowledge_search_index` management commands; per-app test suites, a REST test
  app, and Playwright E2E CI.
- **New settings** — `DJANGO_SPIRE_SEARCH_REGISTRY`, `DJANGO_SPIRE_AUTH_SMS_*`,
  `DJANGO_SPIRE_DEFAULT_THEME_MODE`, `DJANGO_SPIRE_METRIC_VISUAL_REGIONS`,
  `DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX`, `DJANGO_SPIRE_METRIC_RETENTION_DAYS`,
  `DJANGO_SPIRE_METRIC_TRACKING_QUEUE_MAXSIZE`, and
  `DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY`/`SUB_DOMAIN_KEY`.

### Changes

- Dependencies: `django-glue` v0.8.x → v1.0.0, `django` bumped to ≥ 6.0.6, Dandy updated
  for AI model configuration, `robit` pinned to v0.4.9.
- All buttons converted to styled template components; error pages and field/scroll
  templates rewritten.
- View and pagination code refactored to the glue v1 attribute patterns.
- Fonts switched from `.ttf` to `.woff2`; SCSS/CSS packaging consolidated and hardcoded
  colors moved to CSS variables.
- Breadcrumbs standardized across every app via the navigation module.
- Session controller hardened against redefinition and `KeyError` purges.
- Auth group permission data now loads through Glue computed attributes instead of a
  separate template-context payload.
- `multi_file_field.html`, AI chat, and knowledge views updated for `django-glue` v1.0.0.
- Infinite-scroll ordering and filtering can be left empty/overridden on the glue base
  scroll.
- Knowledge, help-desk, comment, notification, file, and REST client broken links and
  breadcrumbs fixed.

### Security

- `AuthUser` admin no longer renders `password` as a plain-text input (editing a user
  previously stored the typed value unhashed).
- MFA codes no longer appear in the `MfaCode` admin list or search, and `MfaCode` is
  read-only; codes can be deleted but not created/edited.
- `ApiAccess` can no longer be created through the admin; keys are generated and hashed
  through the API access form. `ApiAccess.permission` is editable again.
- Notification URLs pointing at `javascript:`/`data:` render as text, and external links
  carry `rel="noopener noreferrer"`.

### Fixes

- Admin `format_html` calls pass url/label as arguments (fixes `TypeError` on Django 6.0).
- Generic foreign key columns in comment, file, history, activity, and viewed admins no
  longer 500 when the related model is not registered in the admin; related objects are
  prefetched to avoid one query per row.
- `ChatMessage.intel` and `Domain`/`SubDomain` admin search no longer raise `FieldError`/
  `ValidationError`; per-row `count()` queries replaced with queryset annotations.
- Bulk tagging in knowledge admins is capped at 25 rows to avoid request timeouts;
  all-read-only admins no longer offer a blank add form.
- Decimal Glue fields accept arbitrary precision; slate select widgets no longer freeze
  the browser on foreign-key choice fields; search-and-select dropdown positioning fixed
  inside modals.
- Help-desk and metric domain/sub-domain services are no longer exposed as deletable Glue
  attributes.
- App notifications and dropdowns restored; `safe_redirect_url` adopted across domain,
  statistic, REST, and task redirects.
- Celery infinite-loop detection hardened; `SessionController` guard and purge fixed.
- Tag rendering bug in the task app, missing login-required decorators on several views,
  and mobile navigation links fixed.
- Seeder OOM issues, LLM error handling, and foreign-key seeding bugs fixed.

### Removals

- `django_spire.sync` and synchronization functionality.
- `django_spire.changelog` app.
- Profiling middleware and `django_spire.theme` app.
- Per-app auth controllers and the `spire_opencode` command.
- `ApiAccessLevelChoices` (replaced by `ApiPermissionChoices`).
- `cache_enabled` from the seeder configuration.
- `distinct` query functionality and tests.
- Hardcoded color values (migrated to CSS variables).

### Upgrade notes

1. Read the breaking-change list above before upgrading; the glue v1 migration and the
   seeding rewrite require the most rework in existing apps.
2. Add `ActivityUserMiddleware` to `MIDDLEWARE` and confirm the system checks are clean.
3. Regenerate or migrate existing seeders to the new field-seeder API.
4. Replace any `javascript:`/`data:` notification URLs and re-issue API keys (old keys
   were hashed under the previous scheme).

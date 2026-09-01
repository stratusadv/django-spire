## v1.1.0 - August 31, 2026

#### Features

- **Metric App** — the `django_spire.metric` application is now feature-complete across domains, statistics, visual metrics, presentations, and signage. (The report module is not part of this release.)

##### Domain

- Domain and sub-domain CRUD pages with admin panels, infinite scrolling, and seeding.
- Sub-domains generate unique, auto-slugged keys on creation.
- Soft-deleting a domain cascades through its sub-domains, statistic groups, and statistics.

##### Statistics

- Statistics organized into groups under a domain, with daily, weekly, and monthly intervals and number, percentage, or currency value types.
- `StatisticValue` rows recorded per reference, sub-domain, and timestamp, indexed for interval and reference lookups and supporting wildcard reference patterns.
- Page-view/click tracking through `StatisticClickMiddleware`, written asynchronously by a background queue worker.
- REST API (`metric/domain/statistic`) to record values and read per-interval totals, summaries, and value lists.
- Aggregations: daily/interval summaries, moving-window averages for percentages, series points, and reference breakdowns.
- `prune_metric_statistic_values` management command enforces retention windows and per-reference tracking caps.
- New settings: `DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY`, `DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY`, `DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX`, `DJANGO_SPIRE_METRIC_RETENTION_DAYS`, and `DJANGO_SPIRE_METRIC_TRACKING_QUEUE_MAXSIZE`.

##### Visual

- Visuals rendered as indicator, line, bar, area, pie, and gauge ECharts, each as a dedicated model sub-class.
- Threshold conditions with state colors (green, blue, yellow, grey, red) and comparison operators including "at or near target" with tolerance.
- References define dataset series per visual.
- Visual regions: named, optionally live-updating (10-second interval) regions rendered on any page via the `render_visual_region` template tag, with connect, update, and disconnect management views.
- New setting: `DJANGO_SPIRE_METRIC_VISUAL_REGIONS`.
- Seeding for domains, statistics, visuals, presentations, and signage.

##### Presentation

- Slide-based presentations with ordered slides and grid-positioned sections that render visuals.

##### Signage

- Signage displays with ordered presentation links, configurable slide display timing and title, and a public display view.

#### Changes

- `statistic_value` and `statistic_value_class` template filters format statistic values by type (number, percentage, currency).

## v1.0.2 - August 29, 2026

#### Fixes

- Fixed broken app notifications
- Fixed broken dropdowns

#### Changes

- Added ability to override and leave empty ordering and filtering for django-glue base `scroll`

## v1.0.1 - August 26, 2026

#### Features

- Glue form widgets display a red asterisk beside labels for required fields.


## v1.0.1-rc4 - August 14, 2026

#### Breaking

- `PortalUserAdmin` moved from `django_spire.auth.group.admin` to `django_spire.auth.user.admin` and renamed `AuthUserAdmin`. It now extends `django.contrib.auth.admin.UserAdmin`.
- `ApiAccess` can no longer be added through the admin. Keys must be created through the API access form so a raw key is generated and hashed.
- `MfaCode` is read-only in the admin. Codes can be deleted but no longer created or edited.
- `SpireModelAdmin` populates `list_select_related` rather than adding foreign keys to `list_filter`, because a foreign key filter loads every related row into the sidebar.

#### Features

- Glue form widgets emit `field-input`, `field-change`, `field-focus`, and `field-blur` events carrying the current and previous field values.
- New `django_spire.contrib.admin.links` helpers: `admin_change_link`, `admin_change_url`, `admin_changelist_url`, `external_link`, and `is_safe_link_url`.
- `SpireModelAdmin` keeps password, secret, token, and key fields out of auto-generated `list_display` and `search_fields`.
- Admin tests cover every registered admin: changelists, searches, filter and sort links, add forms, and change forms. A query-count test fails when a changelist issues one query per row, so a missing `select_related` or `prefetch_related` breaks the build. Rows are built generically, so a newly registered admin needs no fixture.
- Playwright walkthrough of every admin changelist and change form, runnable headed as a demo.

#### Security

- The `AuthUser` admin no longer renders `password` as a plain text input. Editing a user through the admin previously stored the typed value unhashed, locking the account out.
- MFA codes no longer appear in the `MfaCode` admin list or in admin search, so a staff user cannot read a live code.
- `ApiAccess.permission` is editable again. It was listed in `readonly_fields`, so keys were stuck at the `VIEW` default.
- Notification URLs pointing at `javascript:` or `data:` render as text rather than links, and external links carry `rel="noopener noreferrer"` so the opened page cannot reach `window.opener`.

#### Fixes

- Admin `format_html` calls pass the url and label as arguments. A pre-formatted string raises `TypeError: args or kwargs must be provided.` on Django 6.0, and passing arguments escapes both on every supported version.
- Generic foreign key columns in the comment, file, history, activity, and viewed admins no longer raise `NoReverseMatch` and return a 500 when the related model is not registered in the admin.
- `ChatMessage` admin search referenced a nonexistent `content` field, and `Domain` and `SubDomain` search referenced a nonexistent `created_by` field. Both raised `FieldError`.
- The SMS conversation message link filtered on `sms_conversation__id` when the field is named `conversation`, so it returned an unfiltered list.
- `SpireModelAdmin` subclasses configure themselves from their own `model_class` rather than inheriting a parent subclass's generated columns, raise `ValueError` when `model_class` is missing, and no longer override an explicit `list_per_page = 100`.
- Per-row `count()` queries in the AI usage, chat, SMS, knowledge, and auth group admins replaced with queryset annotations.
- Added `list_select_related` to admins rendering foreign key columns, including `temporary_media` on `SmsNotificationAdmin`.
- Generic foreign key columns in the comment, file, history, activity, and viewed admins prefetch `content_object`. `list_select_related` covers only `content_type`, so resolving the object cost one query per row.
- `ChatMessage.intel` falls back to `DefaultMessageIntel` for a malformed `_intel_class_name`. The fallback caught only `ImportError` and `ValidationError`, so a message saved without an intel made `__str__` raise and returned a 500 for the whole changelist.
- The `authenticated_page` Playwright fixture resolves admin URLs with `reverse` rather than assuming `/admin/`, so it works wherever the admin is mounted.
- Bulk tagging actions in the knowledge admins refuse selections above 25 rows. Tagging runs inline, so a larger selection exceeded the request timeout.
- Admins whose fields are entirely read-only no longer offer an add form that would create blank rows.


## v1.0.1-rc3 - August 12, 2026

#### Features

- Added code blocks to the Knowledge editor, including Editor.js support and fenced-code rendering in generated text.
- Knowledge base SMS integration complete — AI SMS conversations can query the knowledge base via SMS, with webhook handling, conversation/message models, admin panels, and intent routing to the `KnowledgeSearchRouter`
- New `DJANGO_SPIRE_AUTH_SMS_` settings to configure SMS integration behavior (throttling, body character lengths, max attempts, expiry, and session duration/idle limits)

#### Fixes

- Decimal Glue form fields now accept arbitrary decimal precision instead of using the browser's default whole-number step.
- Help desk ticket services are no longer exposed as a deletable Glue attribute.


## v1.0.1-rc2 - August 6, 2026

#### Fixes

- Fixed Glue form select widgets causing browser freezes with foreign key choice fields.
- Improved search-and-select dropdown positioning and stacking inside modals.

## 1.0.1-rc1 - August 6, 2026

#### Changes

- Auth group list permission data now loads through Glue queryset computed attributes instead of a separately serialized template context payload
- Domain and subdomain services are no longer exposed as Glue attributes, which was causing a bug
- Updated `multi_file_field.html` to work with `django-glue` v1.0.0.

#### Fixes

- Refactored AI Chat and Knowledge system to work with v1.0.0 and `django-glue` v1.0.0.

## 1.0.0 - July 31, 2026

#### Breaking

- Migrated from `django-glue` v0.8.x to `django-glue` v1.0.0a1 — all templates, views, and glue references updated to new syntax and patterns
- Removed `django_spire.sync` module — synchronization functionality removed
- Removed `django_spire.changelog` app — replaced with `render_markdown` template tag
- Removed profiling middleware module
- Removed `cache_enabled` parameter from seeding system
- Minimum Python version raised to 3.12
- Removed `ApiAccessLevelChoices` — replaced with `ApiPermissionChoices` (level → permission)
- Test project refactored from flat structure to app-based layout
- `set_delete()` method overridden in domain classes
- Removed `distinct` tests (distinct was removed from query handling)

#### Features

- **New App `django_spire.api`** — REST API backend with API key authentication, granular permission levels (view/add/change/delete), and access management UI
- **New App `django_spire.celery`** — Celery task queue support with task tracking, progress monitoring, infinite-loop prevention, and contextual monitoring
- **New App `django_spire.metric.domain`** — Domain/subdomain management with CRUD, admin panels, infinite scrolling, and seeding
- **New App `django_spire.metric.visual`** — Visual metric components (initial structure)
- **New App `django_spire.file`** — Generic file management with uploader/handler module, file seeding, and breadcrumb navigation
- **New Module `django_spire.contrib.rest`** — Django queryset-like pattern for connecting to external REST data sources with Schema/SchemaSet architecture, bearer auth, and prefetch support
- **New Module `django_spire.contrib.converters`** — Utilities to convert Django models to Pydantic classes, data dictionaries, and enums
- **New Module `django_spire.contrib.navigation`** — Navigation utilities extracted from breadcrumb module
- **Seeding System Overhaul** — Complete refactor with new field seeder types (callable, file, index, model, mutate), seed factory pattern, seeding meta system, init/mutate seed logic, and LLM seeding support via `SEEDING_USE_LLM` setting
- **Infinite Scrolling** — Added to domain, subdomain, task pages, and scrollable containers with customizable scroll increments
- **Generic Confirmation Modal Views** — `dispatch_confirmation_modal_form_content` for standardized confirmations (e.g., mark-as-completed)
- **Task Duplication & Interactive Status Updates** — Task app with rich task cards, nested tasks, and interactive status toggling
- **Auth System** — Enforce password change on first login, email lowercase normalization, updated user forms
- **Opencode Integration** — New agents, skills, and management commands for AI-assisted development
- **Button Loading States** — `base_button.html` updated with loading state for `x_button_click` and `button_modal_href`
- **Slide Button Component** — New slide button template
- **Markdown Renderer** — Custom markdown rendering template tag replacing changelog app
- **Django Spire Logo** — Brand logo added
- **Navigation Improvements** — Nav tightening, responsive icons, FOUC prevention, targetable navigation classes
- **View-Level Auth Controllers** — All apps updated with `AppAuthController` permission checks

#### Changes

- Updated `django-glue` requirement from `v0.8.13` → `v0.8.14` → `v1.0.0a1`
- Updated `Dandy` requirement for AI model configuration
- Updated `Robit` to `v0.4.9`
- Switched font files from `.ttf` to `.woff2` for performance
- Replaced all `django_glue` template references with `django_glue_old` during v1 migration, then fully migrated to glue v1 attribute syntax
- Refactored all views and pagination to support glue v1 patterns
- Converted all buttons to styled template components
- SCSS/CSS packaging cleanup — consolidated SCSS compilation, removed hardcoded colors, improved theme variables
- Help desk app — full CRUD refactoring with action buttons, sorting, and breadcrumbs
- Knowledge base — breadcrumb fixes, entity admin panels, delete view fixes, collection navigation improvements
- Comment app — breadcrumb and link fixes
- Notification app — link and breadcrumb fixes
- Breadcrumb system — cleaned up and standardized across all apps
- Domain/subdomain — admin panels, CRUD implementation, glue v1 integration, UI polishing
- Session controller — guard against redefinition, purge fix for `KeyError`
- `Site` object — pull from `DJANGO_SITE_NAME`/`DJANGO_SITE_DOMAIN` env variables
- Added `preconnect` and `defer` for first-page-load performance
- Testing framework — expanded with app-specific test suites, test factories, and REST test app
- CI pipeline — added v1/base branch triggers

#### Fixes

- Celery infinite loop detection and prevention
- Error page templates (`error_page.html`, `scroll.html`)
- Field template (`field.html`) rendering
- Form error rendering and redirect behavior
- Tag bug in task app
- Broken links across help desk, file, comment, notification, knowledge, and domain apps
- Scroll behavior fixes in containers and tasks
- Missing login-required decorators on multiple views
- Auth template/URL issues
- API access form fixes
- Seeding — OOM issues, LLM error handling, FK seeding bugs, multiple FK method support
- Navigation link not working in mobile
- Admin panel many-to-many relationship exclusions
- Report sub-navigation display
- `add_form_activity` verb logic
- Theme CSS and responsive icon fixes
- `toggleLoadingOverlay`/`toggleLoadingSpinner` separation and behavior

#### Removals

- `django_spire.sync` module (functionality removed)
- `django_spire.changelog` app
- Profiling middleware
- `ApiAccessLevelChoices` (replaced by `ApiPermissionChoices`)
- `cache_enabled` from seeder configuration
- `distinct` query functionality and tests
- Hardcoded color values (migrated to CSS variables)

#### Unfinished

- `django_spire.metric.domain` — domain management is functional, visual/metric layer pending
- `django_spire.metric.visual` — initial structure only, not yet feature-complete
